""" Maps views to urls """
from django.urls import path

from . import views

app_name = "auctions"

urlpatterns = [
    path("", views.index, name="index"),
    path("register/", views.register, name="register"),
    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),
    path("create/", views.create, name="create"),
    path("product/<int:product_id>/", views.product_page, name="product"),
    path("bid/", views.make_bid, name="bid"),
    path("add_comment/", views.add_comment, name="add_comment"),
    path("watchlist/", views.watchlist, name="watchlist"),
    path("add_remove_watchlist/", views.add_remove_watchlist,
         name="add_remove_watchlist"),
    path("close_bid/", views.close_bid, name="close_bid"),
    path("owned/", views.owned, name="owned"),
    path("category/<str:category>/", views.display_by_category, name="category")
]
