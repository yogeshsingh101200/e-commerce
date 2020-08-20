""" Views """

from django.http import HttpResponseRedirect, HttpResponseBadRequest
from django.urls import reverse
from django.db import IntegrityError
from django.shortcuts import render
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.db.models import Max

from .models import User, AuctionListing, Bid, Comment, WatchList


@login_required
def index(request):
    """ main route """
    products = AuctionListing.objects.all()
    bids = []
    for product in products:
        bid = product.bids.all().aggregate(Max("bid")).get("bid__max")
        if bid is None:
            bid = product.initial_bid
        bids.append(bid)
    return render(request, "auctions/index.html", {
        "zip_products_bids": zip(products, bids)
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
    product = AuctionListing.objects.get(pk=product_id)
    return render(request, "auctions/product.html", {
        "product": product,
        "bid": product.bids.all().aggregate(Max("bid")).get("bid__max") or product.initial_bid,
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
        bid = record.product.bids.all().aggregate(Max("bid")).get("bid_max")
        if bid is None:
            bid = record.product.initial_bid
        bids.append(bid)
    return render(request, "auctions/index.html", {
        "zip_products_bids": zip(products, bids)
    })


def search_by_category(request):
    """ TODO """
    if request.method == "POST":
        print(request.POST["category"])
        print(AuctionListing.objects.filter(category=request.POST["category"]))
        return render(request, "auctions/category.html", {
            "products": AuctionListing.objects.filter(category=request.POST["category"]),
            "categories": AuctionListing.objects.values_list("category", flat=True).distinct()
        })
    return render(request, "auctions/category.html", {
        "categories": AuctionListing.objects.values_list("category", flat=True).distinct()
    })
