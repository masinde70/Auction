from django_cron import CronJobBase, Schedule
from django.db import IntegrityError, transaction
from datetime import date, timedelta

from auctions.emails import resolve_auction_email
from auctions.models import Auction


class MyCronJob(CronJobBase):
    """
    A Cron job that looks for due auctions every 5 minutes.
    Such auctions will have their state set to auction.models.Auction.STATE_DONE and both author and betters notified.
    """
    RUN_EVERY_MINS = 5  # every 5 minute

    schedule = Schedule(run_every_mins=RUN_EVERY_MINS)
    code = 'auctions.my_cron_job'    # a unique code

    def do(self):
        """
        Atomic insures state cannot be changed while we are working on auctions.
        It also guaranties that all objects load the correct state after the update.
        """
        with transaction.atomic():
            '''
            Get Auctions with state due and deadline <= now - 10min
            '''
            unresolved = Auction.objects.filter(
                persisted_state=Auction.STATE_DUE,
                deadline__lte=date.today() - timedelta(days=1)
            )
            '''
            Notify parties of the auctions conclusion.
            '''
            for auction in unresolved.iterator():
                email = resolve_auction_email(auction)
                auction.send_email(email[0], email[1])
            '''
            Initially ran for loop outside transaction, however it appears
            that the queryset is cleared after update (the length of unresolved is zero).
            This is why we send emails before the update.
            '''
            unresolved.update(persisted_state=Auction.STATE_DONE)
