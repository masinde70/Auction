from django.contrib.auth import  get_user_model
from django.test import client, TestCase
from django.urls import reverse
from datetime import date, timedelta

from .models import Auction, Review

class AuctionTests(TestCase):

    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username='reviewuser',
            email='reviewuser@email.com',
            password='testpass123'
        )


        self.auction = Auction.objects.create(
            title='Bicycle',
            author='Masinde Mtesigwa',
            price='25.00',
            deadline= date.today() + timedelta(days=3),
        )

        self.review = Review.objects.create(
            auction= self.auction,
            author= self.user,
            review='An excellent product',
        )

    def test_auction_listing(self):
        self.assertEqual(f'{self.auction.title}', 'Bicycle')
        self.assertEqual(f'{self.auction.author}', 'Masinde Mtesigwa')
        self.assertEqual(f'{self.auction.price}', '25.00')
        self.assertEqual(f'{self.auction.deadline}', '2019-11-14')

    def test_auction_list_view(self):
        response = self.client.get(reverse('auctions_list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Bicycle')
        self.assertTemplateUsed(response, 'auctions/auctions_list.html')

    def test_auction_detail_view(self):
            response = self.client.get(self.auction.get_absolute_url())
            no_response = self.client.get('/auctions/12345')
            self.assertEqual(response.status_code, 200)
            self.assertEqual(no_response.status_code, 404)
            self.assertContains(response, 'Masinde Mtesigwa')
            self.assertContains(response, 'An excellent product')
            self.assertTemplateUsed(response, 'auctions/auction_detail.html')