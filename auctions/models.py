""" Models """

from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import MinValueValidator
from django.db.models import Max


class User(AbstractUser):
    pass


class AuctionListing(models.Model):
    """ Represents table containing auction listing """
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="products")
    title = models.CharField(max_length=30)
    imageURL = models.TextField(null=True, default=None)
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
    bid = models.IntegerField(default=1, validators=[MinValueValidator(1)])
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="bids")
    product = models.ForeignKey(
        AuctionListing, on_delete=models.CASCADE, related_name="bids")

    def __str__(self):
        """ string representation """
        return f"{self.product.title}: {self.bid}"


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
