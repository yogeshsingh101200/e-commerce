""" Views """

from django.http import HttpResponseRedirect, HttpResponseBadRequest
from django.urls import reverse
from django.shortcuts import render
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.db.models import Max
from django.contrib.auth.forms import AuthenticationForm
from django.contrib import messages

from .models import AuctionListing, Bid, WatchList
from .forms import RegisterForm, BidForm, CommentForm, AuctionListingForm

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


def index(request):
    """ main route """
    if request.method == "POST" and request.POST["category"] != "All":
        products = AuctionListing.objects.filter(
            category=request.POST["category"]).filter(buyer=None)
        selected = request.POST["category"]
    else:
        products = AuctionListing.objects.filter(buyer=None)
        selected = None

    bids = []
    for product in products:
        bid = product.bids.all().aggregate(Max("bid")).get("bid__max")
        bids.append(bid)
    return render(request, "auctions/index.html", {
        "zip_products_bids": zip(products, bids),
        "categories": categories,
        "selected": selected,
        "title": "Active Listing"
    })


def register(request):
    """ Register a user to website """
    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return HttpResponseRedirect(reverse("auctions:index"))
        return render(request, "auctions/register.html", {
            "form": form
        })
    return render(request, "auctions/register.html", {
        "form": RegisterForm()
    })


def login_view(request):
    """ Logins a user """
    if request.method == "POST":
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return HttpResponseRedirect(request.POST["next"])
        return render(request, "auctions/login.html", {
            "next": request.POST.get("next") or reverse("auctions:index"),
            "form": form
        })
    return render(request, "auctions/login.html", {
        "next": request.GET.get("next") or reverse("auctions:index")
    })


def logout_view(request):
    """ Logout a user """
    logout(request)
    return HttpResponseRedirect(reverse('auctions:login'))


@login_required
def create(request):
    """ Creates listing """
    if request.method == "POST":
        form = AuctionListingForm(request.POST)
        if form.is_valid():
            product = form.save(commit=False)
            product.user = request.user
            product.save()
            bid = Bid(user=request.user,
                      bid=form.cleaned_data["initial_bid"], product=product)
            bid.save()
            return HttpResponseRedirect(reverse("auctions:index"))
        return render(request, "auctions/create.html", {
            "categories": categories,
            "form": form
        })
    return render(request, "auctions/create.html", {
        "categories": categories
    })


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
        "in_watchlist": product.watchlist.filter(
            user=request.user) if request.user.is_authenticated else False,
        "form": BidForm()
    })


# @login_required
def make_bid(request):
    """ Make bid """
    if request.method == "POST":
        if not request.user.is_authenticated:
            messages.add_message(request, messages.ERROR,
                                 "Your need to login/register to place bid!",
                                 extra_tags="bid_form_error")
            return HttpResponseRedirect(reverse("auctions:product",
                                                args=(request.POST.get("product"),)))
        form = BidForm(request.POST)
        if form.is_valid():
            bid = form.save(commit=False)
            bid.user = request.user
            bid.save()
        else:
            for field in form:
                for error in field.errors:
                    messages.add_message(
                        request, messages.ERROR, error, extra_tags="bid_form_error")
            for error in form.non_field_errors():
                messages.add_message(
                    request, messages.ERROR, error, extra_tags="bid_form_error")
        return HttpResponseRedirect(reverse("auctions:product",
                                            args=(form.cleaned_data["product"].pk,)))
    return HttpResponseBadRequest(f"This method cannot handle method {request.method}", status=405)


# @login_required
def add_comment(request):
    """ Adds comment """
    if request.method == "POST":
        if not request.user.is_authenticated:
            messages.add_message(request, messages.ERROR,
                                 "Your need to login/register to comment!",
                                 extra_tags="comment_form_error")
            return HttpResponseRedirect(reverse("auctions:product",
                                                args=(request.POST.get("product"),)))
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.user = request.user
            comment.save()
        else:
            for field in form:
                for error in field.errors:
                    messages.add_message(
                        request, messages.ERROR, error, extra_tags="comment_form_error")
            for error in form.non_field_errors():
                messages.add_message(
                    request, messages.ERROR, error, extra_tags="comment_form_error")
        return HttpResponseRedirect(reverse("auctions:product",
                                            args=(form.cleaned_data["product"].pk,)))

    return HttpResponseBadRequest(f"This method cannot handle method {request.method}", status=405)


def add_remove_watchlist(request):
    """ Adds/remove product to/from watchlist """
    if request.method == "POST":
        if not request.user.is_authenticated:
            messages.add_message(request, messages.ERROR,
                                 "Your need to login/register to add to watchlist!",
                                 extra_tags="watchlist_form_error")
            return HttpResponseRedirect(reverse("auctions:product",
                                                args=(request.POST.get("product"),)))
        data = request.POST
        product = AuctionListing.objects.get(pk=data["product"])
        if product.watchlist.filter(user=request.user):
            product.watchlist.filter(user=request.user).delete()
        else:
            watchlist_item = WatchList(product=product, user=request.user)
            watchlist_item.save()
        return HttpResponseRedirect(reverse("auctions:product", args=(data["product"],)))
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
        "zip_products_bids": zip(products, bids),
        "categories": categories,
        "selected": None,
        "title": "Watchlist"
    })


@login_required
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


@login_required
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
        "selected": None,
        "title": "Owned Items"
    })
