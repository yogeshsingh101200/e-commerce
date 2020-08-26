""" Views """

from django.http import HttpResponseRedirect, HttpResponseBadRequest
from django.urls import reverse
from django.db import IntegrityError
from django.shortcuts import render
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.db.models import Max

from .models import User, AuctionListing, Bid, Comment, WatchList

categories = [
    "Appliances",
    "Beauty",
    "Books",
    "Electronics",
    "Fashion",
    "Fitness",
    "Furniture",
    "Sports",
    "Toys",
    "Other"
]


@login_required
def index(request):
    """ main route """
    if request.method == "POST" and request.POST["category"] != "All":
        products = AuctionListing.objects.filter(
            category=request.POST["category"])
        selected = request.POST["category"]
    else:
        products = AuctionListing.objects.all()
        selected = None

    bids = []
    for product in products:
        bid = product.bids.all().aggregate(Max("bid")).get("bid__max")
        bids.append(bid)
    return render(request, "auctions/index.html", {
        "zip_products_bids": zip(products, bids),
        "categories": categories,
        "selected": selected
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
        next_url = request.POST.get("next")
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            if next_url:
                return HttpResponseRedirect(next_url)
            return HttpResponseRedirect(reverse("auctions:index"))
    return render(request, "auctions/login.html", {
        "next": request.GET.get("next")
    })


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
        url = data["url"]
        product = AuctionListing(user=request.user, title=title,
                                 description=description, category=category, imageURL=url)
        product.save()
        bid = Bid(user=request.user, bid=initial_bid, product=product)
        bid.save()
        return HttpResponseRedirect(reverse("auctions:index"))
    return render(request, "auctions/create.html", {
        "categories": categories
    })


@login_required
def product_page(request, product_id):
    """ Product page """
    product = AuctionListing.objects.get(pk=product_id)
    max_bid = product.bids.all().aggregate(Max("bid")).get("bid__max")
    max_bidder = product.bids.get(bid=max_bid).user
    return render(request, "auctions/product.html", {
        "product": product,
        "bid": max_bid,
        "max_bidder": max_bidder,
        "comments": product.comments.all(),
        "in_watchlist": product.watchlist.filter(user=request.user)
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


def add_comment(request):
    """ Adds comment """
    if request.method == "POST":
        data = request.POST
        content = data["content"]
        product = AuctionListing.objects.get(pk=request.POST["product"])
        comment = Comment(content=content, user=request.user, product=product)
        comment.save()
        return HttpResponseRedirect(reverse("auctions:product", args=(request.POST["product"],)))
    return HttpResponseBadRequest(f"This method cannot handle method {request.method}", status=405)


@login_required
def watchlist(request):
    """ Displays user watchlist and also adds/remove product to/from watchlist """
    if request.method == "POST":
        data = request.POST
        product = AuctionListing.objects.get(pk=data["product"])
        if product.watchlist.filter(user=request.user):
            product.watchlist.filter(user=request.user).delete()
        else:
            watchlist_item = WatchList(product=product, user=request.user)
            watchlist_item.save()
        return HttpResponseRedirect(reverse("auctions:product", args=(data["product"],)))

    records = request.user.watchlist.all()
    products = []
    bids = []
    for record in records:
        products.append(record.product)
        bid = record.product.bids.all().aggregate(Max("bid")).get("bid__max")
        bids.append(bid)
    return render(request, "auctions/index.html", {
        "zip_products_bids": zip(products, bids)
    })


def close_bid(request):
    """ Sold Item """
    if request.method == "POST":
        product = AuctionListing.objects.get(pk=request.POST["product"])
        max_bid = product.bids.all().aggregate(Max("bid")).get("bid__max")
        bid = product.bids.get(bid=max_bid)
        user = bid.user
        product.buyer = user
        product.save()
        return HttpResponseRedirect(reverse("auctions:product", args=(request.POST["product"],)))
    return HttpResponseBadRequest(f"This method cannot handle method {request.method}", status=405)


def owned(request):
    """ Displays items owned """
    products = request.user.owner.all()
    bids = []
    for product in products:
        bid = product.bids.all().aggregate(Max("bid")).get("bid__max")
        bids.append(bid)
    return render(request, "auctions/index.html", {
        "zip_products_bids": zip(products, bids),
        "categories": categories,
        "selected": None
    })
