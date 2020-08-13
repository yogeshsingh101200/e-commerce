""" Views """

from django.http import HttpResponseRedirect, HttpResponseBadRequest
from django.urls import reverse
from django.db import IntegrityError
from django.shortcuts import render
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required

from .models import User, AuctionListing, Bid


@login_required
def index(request):
    """ main route """
    return render(request, "auctions/index.html", {
        "list": AuctionListing.objects.all()
    })


def register(request):
    """ Register a user to website """
    if request.method == "POST":
        username = request.POST["username"]
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "auctions/resgister.html")
        try:
            user = User.objects.create_user(username, password=password)
        except IntegrityError:
            return render(request, "auctions/register.html", {
                "message": "Invalid credentials!"
            })
        login(request, user)
        return HttpResponseRedirect(reverse("auctions:index"))
    return render(request, "auctions/register.html")


def login_view(request):
    """ Logout a user """
    if request.method == "POST":
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            if request.GET.get("next"):
                return HttpResponseRedirect(request.GET["next"])
            return HttpResponseRedirect(reverse("auctions:index"))
    return render(request, "auctions/login.html")


def logout_view(request):
    """ Logout a user """
    logout(request)
    return HttpResponseRedirect(reverse('auctions:login'))


def create(request):
    """ Creates listing """
    if request.method == "POST":
        data = request.POST
        title = data["title"]
        description = data["description"]
        initial_bid = data["initial_bid"]
        category = data["category"]
        product = AuctionListing(user=request.user, title=title, description=description,
                                 initial_bid=initial_bid, category=category)
        product.save()
        return HttpResponseRedirect(reverse("auctions:index"))
    return render(request, "auctions/create.html")


def product_page(request, product_id):
    """ Product page """
    bids = Bid.objects.filter(
        product=AuctionListing.objects.get(pk=product_id))
    return render(request, "auctions/product.html", {
        "product": AuctionListing.objects.get(pk=product_id),
        "bid": max([bid.bid for bid in bids])
    })


def make_bid(request):
    """ Make bid """
    if request.method == "POST":
        bid_amnt = request.POST["bid"]
        product = AuctionListing.objects.get(pk=request.POST["product"])
        bid = Bid(bid=bid_amnt, user=request.user, product=product)
        bid.save()
        return HttpResponseRedirect(reverse("auctions:product", args=(request.POST["product"],)))
    return HttpResponseBadRequest(f"This method cannot handle method {request.method}", status=405)
