from django.urls import path, re_path

from . import views
from .views import *


urlpatterns = [
    path('new/', AuctionsCreateView.as_view(), name='auctions_create'),
    path('confirm/', AuctionsConfirmView.as_view(), name='auctions_confirm'),
    path('', AuctionsListView.as_view(), name='auctions_list'),
    path('<uuid:pk>', AuctionsDetailView.as_view(), name='auction_detail'),
    path('<pk>bid/', BidView.as_view(), name='bid'),
    path('<uuid:pk>/delete/', AuctionDeleteView.as_view(), name='auction_delete'),
    path('search/', SearchResultsListView.as_view(), name='search_results'),
    path('languages/edit', LanguageUpdateView.as_view(), name='language_update'),
    path('<pk>/update', AuctionUpdate.as_view(), name='auction_update'),
    path('<uuid:id>ban/', BanView.as_view(), name='ban'),
    path('cron/', AuctionCronView.as_view(), name='crontasks'),
    path('resolve/', resolve, name='resolve'),
]
