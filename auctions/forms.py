""" Forms """

from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User, Bid, Comment, AuctionListing


class RegisterForm(UserCreationForm):
    """ Form to register user """
    class Meta(UserCreationForm.Meta):
        model = User


class BidForm(forms.ModelForm):
    """ maps to bid model """
    class Meta:
        model = Bid
        fields = ["bid", "product"]


class CommentForm(forms.ModelForm):
    """ maps to Comment model """
    class Meta:
        model = Comment
        fields = ["content", "product"]


class AuctionListingForm(forms.ModelForm):
    """ maps to auction listing model """
    initial_bid = forms.IntegerField()

    class Meta:
        model = AuctionListing
        fields = ["title", "imageURL", "description", "category"]
