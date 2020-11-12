from django.contrib import admin

from .models import *


class ReviewInline(admin.TabularInline):
    model = Review


class AuctionsAdmin(admin.ModelAdmin):
    inlines = [
        ReviewInline,
    ]
    list_display = ("title", "description","author", "price", "deadline")



class BidAdmin(admin.ModelAdmin):
    list_display = ('auction', 'bidder', 'amount')

    class Meta:
        model = Bid


admin.site.register(Bid, BidAdmin)
admin.site.register(Auction, AuctionsAdmin)
