from django.urls import path

from .views import AuctionAPIView, AuctionAPIDetail

urlpatterns = [
    path('<int:pk>', AuctionAPIDetail.as_view()),
    path('', AuctionAPIView.as_view()),
]