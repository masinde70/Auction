from datetime import datetime

from django.forms import ModelForm, BooleanField, HiddenInput, forms
from .models import Auction, Bid
from django import forms


class AuctionForm(ModelForm):
    confirmed = BooleanField(
        required=False,
        initial=False,
        help_text='whether the form has been confirmed',
        widget=HiddenInput
    )
    now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    deadline = forms.DateTimeField(required=True, label='End date',
                                   help_text="Minimum 72 hours duration from now '%s'" % now,
                                   widget=forms.TextInput(
                                       attrs={'placeholder': "Deadline"}
                                   )
                                   )

    class Meta:
        model = Auction
        fields = ["title", "description", "price", "deadline"]

    def save(self, commit=True, *args, **kwargs):
        user = kwargs.pop('user') if 'user' in kwargs else None
        auction = super(AuctionForm, self).save(commit=False, *args, **kwargs)
        if getattr(auction, 'author', None) is None and user is not None:
            auction.author = user

        if commit:
            auction.save()
        return auction


class AuctionEditForm(forms.Form):
    description = forms.CharField(max_length=400, label='Description',
                                  widget=forms.Textarea(
                                      attrs={'placeholder': 'Write item description update.',
                                             'cols': '200', 'rows': '10'}
                                  )
                                  )

    class Meta:
        model = Auction
        fields = ('description',)


class BidForm(forms.Form):
    bid = forms.DecimalField(max_digits=20, decimal_places=2)


