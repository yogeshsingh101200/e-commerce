""" register models """

from django.contrib import admin

from .models import User, AuctionListing, Bid


admin.site.register(User)
admin.site.register(AuctionListing)
admin.site.register(Bid)
