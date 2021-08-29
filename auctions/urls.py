from os import name
from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("auction/<int:auction_id>", views.auction, name="auction"),
    path("categories/<str:categories>", views.categories, name="categories"),
    path("comments", views.comment, name="comment"),
    path("categories", views.category_list, name="category_list"),
    path("watchlist", views.watchlist, name="watchlist"),
    path("bid", views.bid, name="bid"),
    path("add_watchlist", views.add_watchlist, name="add_watchlist"),
    path("new_listing", views.new_listing, name="new_listing"),
    path("user_auctions", views.user_auctions, name="user_auctions"),
    path("user_bids", views.user_bids, name="user_bids"),
    path("accounts/login/", views.login_view, name="login"),
    path("accounts/logout/", views.logout_view, name="logout"),
    path("accounts/register/", views.register, name="register")
]

