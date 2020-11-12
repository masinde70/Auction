from django_cron import CronJobBase, Schedule
from django.db import IntegrityError, transaction
from datetime import date

from auctions.models import Auction


class MyDueCronJob(CronJobBase):
    """
    A Cron job that looks for active auctions with deadline in the passed.
    Such auctions will have their state set to auction.models.Auction.STATE_DUE.
    The job runs every minute.
    """
    RUN_EVERY_MINS = 1  # every 1 minute

    schedule = Schedule(run_every_mins=RUN_EVERY_MINS)
    code = 'auction.my_due_cron_job'    # a unique code

    def do(self):
        try:
            '''
            atomic insures state cannot be changed while we are working on auctions.
            It also guaranties that all objects load the correct state after the update.
            '''
            with transaction.atomic():
                '''
                Get Auctions with state active and deadline <= now
                '''
                unresolved = Auction.objects.filter(
                    persisted_state=Auction.STATE_ACTIVE,
                    deadline__lte=date.today()    # lte == less than or equal
                )
                '''
                Change state of unresolved auctions to due state.
                The auction is then due for adjudication.
                '''
                unresolved.update(persisted_state=Auction.STATE_DUE)
        except IntegrityError:
            pass
