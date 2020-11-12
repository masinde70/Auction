import uuid
from django.core.exceptions import PermissionDenied
from django.core.validators import MinValueValidator, DecimalValidator
from django.db import models, IntegrityError
from datetime import datetime
from django.core.mail import send_mail
from django.contrib.auth.models import Permission
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.utils import timezone
from .validators import *
from .exptns import *


class Auction(models.Model):
    id = models.UUIDField(primary_key=True,default=uuid.uuid4,editable=False)
    title = models.CharField(max_length=200)
    description = models.TextField(max_length=1000, help_text="Precise description of item(s)")
    author = models.ForeignKey(get_user_model(),on_delete=models.CASCADE,)
    price = models.DecimalField(max_digits=6,decimal_places=2,validators=[MinValueValidator(0.00)])
    deadline = models.DateField(verbose_name="dead line",validators=[validate_3_days_from_now])
    state = models.IntegerField(default=0)
    created = models.DateTimeField(auto_now_add=True, editable=False)
    last_modified = models.DateTimeField(auto_now=True,editable=False)
    version = models.IntegerField(default=0, help_text="Newest version")

    class Meta:
        permissions = [
            ("special_status", "can read all auctions, Can add auction"),
        ]

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('auction_detail', args=[str(self.id)])

    def is_author(self, user):
        return user == self.author

    class State:
        def __init__(self, auction):
            self._auction = auction

            self._initialized = datetime.now()


class Review(models.Model):
    auction = models.ForeignKey(Auction,on_delete=models.CASCADE, related_name='reviews')
    review = models.CharField(max_length=255)
    author = models.ForeignKey(get_user_model(),on_delete=models.CASCADE,)

    def __str__(self):
        return self.review


class Bid(models.Model):
    auction = models.ForeignKey(Auction, on_delete=models.CASCADE)
    bidder = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=20, decimal_places=2)

