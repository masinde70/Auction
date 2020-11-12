from rest_framework import serializers

from auctions.models import *


class AuctionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Auction
        fields = (
            'id',
            'title',
            'deadline',
            'price',
            'created',
        )


class BidSerializer(serializers.ModelSerializer):
    class Meta:
        model = Bid
        fields = (
            'auction',
            'amount',
            'bidder',
            'created',
        )
