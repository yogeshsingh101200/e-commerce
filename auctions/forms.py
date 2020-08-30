""" Forms """

from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User, Bid


class RegisterForm(UserCreationForm):
    """ Form to register user """
    class Meta(UserCreationForm.Meta):
        model = User


class BidForm(forms.ModelForm):
    """ maps to bid model """
    class Meta:
        model = Bid
        fields = "__all__"
