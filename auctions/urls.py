""" Maps views to urls """
from django.urls import path

from . import views

app_name = "auctions"

urlpatterns = [
    path("", views.index, name="index"),
    path("register", views.register, name="register"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("create", views.create, name="create"),
    path("product/<int:product_id>", views.product_page, name="product"),
    path("bid", views.make_bid, name="bid"),
    path("add_comment", views.add_comment, name="add_comment")
]
