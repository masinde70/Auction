from rest_framework import generics
from auctions.models import *
from .serializers import AuctionSerializer

class AuctionAPIView(generics.ListCreateAPIView):
    queryset = Auction.objects.all()
    serializer_class = AuctionSerializer

class AuctionAPIDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Auction.objects.all()
    serializer_class = AuctionSerializer