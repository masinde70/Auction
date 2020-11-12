from decimal import Decimal
from uuid import uuid4
from django.contrib import messages
from django.db.models import Q
from django.contrib.auth.mixins import *
from django.core.exceptions import *
from django.db import *
from django.shortcuts import get_object_or_404, render, redirect
from django.urls import *
from django.views import *
import logging
from datetime import datetime
from django.core.exceptions import ObjectDoesNotExist
from django.views.generic import *
from django.views.generic.edit import CreateView, DeleteView, FormMixin
from django.http import Http404, HttpResponseRedirect, HttpResponseForbidden
from .models import *
from .forms import AuctionForm, BidForm
from .exptns import *
from django.core.mail import send_mail
from .emails import *
from django.utils import translation
from django.conf import settings
from .cron import *
from .mydue import *

from django.utils.translation import gettext as _

LANGUAGE_SESSION_KEY = '_language'


class AuctionsListView(LoginRequiredMixin, ListView):
    model = Auction
    context_object_name = 'auction_list'
    template_name = 'auctions/auctions_list.html'
    login_url = 'account_login'


class AuctionsDetailView(LoginRequiredMixin, DetailView):
    model = Auction
    context_object_name = 'auction'
    template_name = 'auctions/auction_detail.html'
    login_url = 'account_login'
    permission_required = 'auctions.special_status'


class SearchResultsListView(ListView):
    model = Auction
    context_object_name = 'auction_list'
    template_name = 'auctions/search_results.html'

    def get_queryset(self):
        query = self.request.GET.get('q')
        if query:
            return Auction.objects.filter(title__icontains=query).filter(state=0)
        else:
            return Auction.objects.filter(state=0)


class AuctionsCreateView(LoginRequiredMixin, CreateView):
    form_class = AuctionForm
    template_name = 'auctions/auctions_create.html'

    def form_valid(self, form):
        for field in form.fields:
            form.fields[field].widget.attrs['readonly'] = True
            self.template_name = 'auctions/auctions_confirm.html'
            return super(AuctionsCreateView, self).form_invalid(form)


class AuctionsConfirmView(AuctionsCreateView):
    def form_valid(self, form):
        self.object = form.save(user=self.request.user)
        return FormMixin.form_valid(self, form)


class AuctionUpdate(LoginRequiredMixin, UpdateView):
    model = Auction
    fields = [
        "title",
        "description",
        "price",
        "deadline"
    ]
    template_name_suffix = '_update_form'
    success_url = "/"

    def dispatch(self, request, *args, **kwargs):
        obj = self.get_object()
        if obj.author != self.request.user:
            #return HttpResponseForbidden()
            #messages.error(request, 'This is not your auction to edit')
            return redirect(obj)

        return super(AuctionUpdate, self).dispatch(request, *args, **kwargs)


class AuctionDeleteView(LoginRequiredMixin, DeleteView):
    model = Auction
    success_url = reverse_lazy('auction_list')


class LanguageUpdateView(View):
    def get(self, request):
        language = request.GET.get('lang', 'sw')
        translation.activate(language)
        next_page = request.GET.get('next', reverse('home'))
        if language and translation.check_for_language(language):
            if hasattr(request, 'session'):
                request.session[LANGUAGE_SESSION_KEY] = language
            else:
                next_page.set_cookie(settings.LANGUAGE_COOKIE_NAME, language,
                                     max_age=settings.LANGUAGE_COOKIE_AGE,
                                     path=settings.LANGUAGE_COOKIE_PATH,
                                     domain=settings.LANGUAGE_COOKIE_DOMAIN)

        response = HttpResponseRedirect(next_page)

        return response



def make_bid(auction, bidder, amount):
    decimal_bid_amount = Decimal(amount).quantize(Decimal('0.01'))
    highest_bid = None
    try:
        highest_bid = auction.bid_set.latest('amount')
    except ObjectDoesNotExist:
        pass

    if highest_bid and highest_bid.amount >= decimal_bid_amount or auction.price > Decimal(
            amount):
        message = 'New bid must be greater than the current bid for at least 0.01'
    elif bidder.id is auction.author.id:
        message = "You cannot bid on your own auctions"
    elif auction.state == 1:
        message = "You can only bid on active auctions"
    elif auction.state == 3:
        message = "You can only bid on active auctions"

    else:
        auction.bid_set.create(bidder=bidder, amount=amount)

        send_mail(
            'New bin on YAAS',
            'Hello, there is a new bin on your auction on YAAS',
            'yaas@yaas.com',
            [auction.author.email],
            fail_silently=False,
        )
        if highest_bid:
            send_mail(
                'Overbidden on YAAS',
                'Hello you have bin overbidden on YAAS',
                'yaas@yaas.com',
                [highest_bid.bidder.email],
                fail_silently=False,
            )
        message = "success"
    return message



class BidView(LoginRequiredMixin, View):
    form_class = BidForm
    template_name = 'auctions/bid.html'

    def post(self, request, pk):
        form = self.form_class(request.POST)
        auction = get_object_or_404(Auction, pk=pk)
        bids = auction.bid_set.all()
        message = ""
        if form.is_valid():
            amount = form.cleaned_data['bid']
            edited_auction_version = request.POST.get('auction_version', False)
            if int (edited_auction_version) < auction.version:
                message = "The description was edited or  before bid, check it before you bid again"
            else:
                message = make_bid(auction, request.user, amount)
                if message == "success":
                    messages.success(request, 'You has bid successfully')
                    return redirect("home")

        form.add_error('bid', message)

        return render(request, self.template_name, {
            'form': form,
            'auction': auction,
            'bids': bids
        })



class BanView(LoginRequiredMixin, UserPassesTestMixin, View):
    def test_func(self):
        return self.request.user.is_staff

    def post(self, request, id):
        auction = get_object_or_404(Auction, pk=id)
        auction.state = 1
        auction.save()
        bids = auction.bid_set.all()
        send_mail(
            'Banned auction on YAAS',
            'Hello, your auction has been banned on YAAS',
            'yaas@yaas.com',
            [auction.author.email],
            fail_silently=False,
        )
        for bid in bids:
            send_mail(
                'Auction banned on YAAS',
                'Hello, an auction you bid on has been banned on YAAS',
                'yaas@yaas.com',
                [bid.bidder.email],
                fail_silently=False,
            )
        messages.success(request, 'Ban successfully')
        return redirect("auction_detail", pk=id)
    pass

class AuctionCronView(LoginRequiredMixin, View):
    template_nam = 'auctions/crontasks.html'
    def croon(self, res):
        res = MyCronJob()
        return res


def resolve(request):
    now = timezone.now()
    auctions = Auction.objects.filter(deadline=now).filter(state=0)
    if auctions.exists():
        for auction in auctions:
            auction.state = 3
            auction.save()

            send_mail('They auction time has ended',
                  'yaas@yaas.com',
                  [auction.author.email],
                  fail_silently=False,
                  )

            bids = auction.bid_set.all()
            if bids.exists():
                for bid in bids:
                    send_mail(
                    'The auction your bidding has ended',
                    [bid.bidder.email],
                    fail_silently=False,
                )
    return redirect("home")