""" Models """

from django.db import models
from django.core.exceptions import ValidationError
from django.contrib.auth.models import AbstractUser
from django.db.models import Max
from django.utils.translation import gettext_lazy as _


class User(AbstractUser):
    pass


class AuctionListing(models.Model):
    """ Represents table containing auction listing """
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="products")
    title = models.CharField(max_length=50)
    imageURL = models.URLField(null=True, blank=True)
    description = models.TextField()
    category = models.CharField(max_length=10)
    buyer = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="owner", null=True)

    def __str__(self):
        """ string representation """
        max_bid = self.bids.all().aggregate(Max("bid")).get("bid__max")
        return f"{self.title}: Max Bid {max_bid}"


class Bid(models.Model):
    """ Represents bids table """
    bid = models.IntegerField()
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="bids")
    product = models.ForeignKey(
        AuctionListing, on_delete=models.CASCADE, related_name="bids")

    def __str__(self):
        """ string representation """
        return f"{self.product.title}: {self.bid}"

    def clean(self):
        """ validates if placed bid is more than highest bid """
        max_bid = self.product.bids.all().aggregate(
            Max("bid")).get("bid__max")
        if self.bid and self.bid <= max_bid:
            raise ValidationError(_(f"Place bid higher than {max_bid}!"))


class Comment(models.Model):
    """ Represents comments table """
    content = models.TextField()
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="comments")
    product = models.ForeignKey(
        AuctionListing, on_delete=models.CASCADE, related_name="comments")

    def __str__(self):
        """ string representation """
        return f"{self.user}"


class WatchList(models.Model):
    """ Represents watchlist table """
    product = models.ForeignKey(
        AuctionListing, on_delete=models.CASCADE, related_name="watchlist")
    user = models.ForeignKey(User, on_delete=models.CASCADE,
                             related_name="watchlist")

    def __str__(self):
        """ string representation """
        return f"{self.product}: {self.user}"
