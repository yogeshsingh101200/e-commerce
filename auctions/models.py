""" Models """

from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import MinValueValidator


class User(AbstractUser):
    pass


class AuctionListing(models.Model):
    """ Represents table containing auction listing """
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="products")
    title = models.CharField(max_length=30)
    imageURL = models.TextField(null=True, default=None)
    description = models.TextField()
    initial_bid = models.IntegerField(
        default=1, validators=[MinValueValidator(1)])
    category = models.CharField(max_length=10)
    buyer = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="owner", null=True)


class Bid(models.Model):
    """ Represents bids table """
    bid = models.IntegerField()
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="bids")
    product = models.ForeignKey(
        AuctionListing, on_delete=models.CASCADE, related_name="bids")


class Comment(models.Model):
    """ Represents comments table """
    content = models.TextField()
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="comments")
    product = models.ForeignKey(
        AuctionListing, on_delete=models.CASCADE, related_name="comments")


class WatchList(models.Model):
    """ Represents watchlist table """
    product = models.ForeignKey(
        AuctionListing, on_delete=models.CASCADE, related_name="watchlist")
    user = models.ForeignKey(User, on_delete=models.CASCADE,
                             related_name="watchlist")
