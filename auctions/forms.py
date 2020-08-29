""" Forms """

from django.contrib.auth.forms import UserCreationForm
from .models import User


class RegisterForm(UserCreationForm):
    """ Form to register user """
    class Meta(UserCreationForm.Meta):
        model = User
