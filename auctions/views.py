from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.db.models.expressions import Exists
from django.http import HttpResponse, HttpResponseRedirect, request
from django.shortcuts import render
from django.urls import reverse
from django.contrib.auth.decorators import login_required

from .models import Bid, Comments, User, auctions, WatchList



text = {
    "added": "Added from watchlist",
    "removed":"Removed from watchlist",
    "active_status": "active",
    "closed_status": "closed",
}


def index(request):
    auctions_list = auctions.objects.all().filter(status=text["active_status"])
    return render(request, "auctions/index.html", {
        "auctions": auctions_list
    })


def categories(request, categories):
    category_list = auctions.objects.filter(category=categories)
    return render (request, "auctions/categories.html", {
        "auctions":category_list,
        "category":categories
    })


def category_list(request):
    category_list = auctions.objects.filter(status=text["active_status"]).values_list("category", flat=True).distinct()
    return render(request, "auctions/category_list.html",{
        "category_list":category_list
    })


@login_required
def comment(request):
    if request.method == "POST":
        item_id = request.POST.get("auction_id")
        comments = request.POST.get("comment")
        item = auctions.objects.get(id=item_id)
        user_comment = Comments(user=request.user, comment=comments, item=item)
        user_comment.save()
        return auction(request, item_id)
    else:
        return index(request)


@login_required
def add_watchlist(request):
    if request.method == "POST":
        item = request.POST.get("item_id")
        item_id = auctions.objects.get(id=item)
        watchlist_cart = WatchList.objects.all()

        if not watchlist_cart:
                watchlist = WatchList(item=item_id, user=request.user)
                watchlist.save()
                return auction(request, item, message=text["added"])
        else: 
            try:
                user_item = WatchList.objects.get(user=request.user, item=item_id)
            except WatchList.DoesNotExist:
                watchlist = WatchList(item=item_id, user=request.user)
                watchlist.save()
                return auction(request, item, message=text["added"])
            

            WatchList.objects.filter(user=request.user, item=item_id).delete()
            return auction(request, item, message=text["removed"])
    else:
        return HttpResponseRedirect(reverse("index"))


@login_required
def user_auctions(request):
    if request.method == "GET":
        user_auctions = auctions.objects.filter(user=request.user, status=text["active_status"])
        user_auctions_id = auctions.objects.filter(user=request.user).values_list("id", flat=True)
        max_bid = Bid.objects.all()
        bid_data = {}

        for value in user_auctions_id:
            bids_container = []
            for i in max_bid:
                if i.item == auctions.objects.get(id=value):
                    bids_container.append(i.bid)
                    sorted_bids = sorted(bids_container, reverse=True)
                    bid_data[f"{value}"] = sorted_bids
      
        return render(request, "auctions/user_auction.html", {
            "auctions":user_auctions,
            "bid_data":bid_data
        })
    else:
        auction_id = request.POST.get("auction_id")
        auction = auctions.objects.get(id=auction_id)
        auction.status = "closed"
        auction.save()
        return HttpResponseRedirect(reverse("user_auctions"))



@login_required
def user_bids(request):
    all_bids = Bid.objects.all().values("item", "bid", "user")
    user_bids = Bid.objects.filter(user=request.user).values("item", "bid")
    item_id = Bid.objects.filter(user=request.user).values_list("item", flat=True).distinct()

    general_bid_data = {}
    user_bid_data = {}
    for user_bid in user_bids:
        general_bids_container = []
 
        if str(user_bid["item"]) not in user_bid_data:
            user_bids_container = [user_bid["bid"]]
            user_bid_data[f"{user_bid['item']}"] = user_bids_container
        else:
            user_bids_container.append(user_bid["bid"])
            sorted_bids = sorted(user_bids_container, reverse=True)
            user_bid_data[f"{user_bid['item']}"] = sorted_bids
    
        for all_bid in all_bids:
            if user_bid["item"] == all_bid["item"]: 
                general_bids_container.append(all_bid["bid"])
                sorted_bids = sorted(general_bids_container, reverse=True)
                general_bid_data[f"{user_bid['item']}"] = sorted_bids

    status = {}
    for general_item, general_bids in general_bid_data.items():
        for user_item, item_bid in user_bid_data.items():
            if general_item == user_item:
                if general_bids[0] == item_bid[0]:
                    status[general_item] = "Highest Bid"
                else:
                    status[user_item] = "Not the highest bid"
        

    item = auctions.objects.filter(id__in=item_id)

    return render(request, "auctions/user_bid.html", {
        "auctions": item,
        "item_id": item_id,
        "status":status,
        "general_bid_dict":general_bid_data,
        "user_bid_dict":user_bid_data
    })

@login_required
def watchlist(request):
    watchlist = WatchList.objects.filter(user=request.user).values_list("item", flat=True)
    items = auctions.objects.filter(id__in=watchlist, status=text["active_status"])
    return render(request, "auctions/watchlist.html", {
        "watchlist":items
    })

    
@login_required
def bid(request):
    if request.method == "POST":
        item_id = request.POST.get("item_id")
        item = auctions.objects.get(id=item_id)
        value = request.POST.get("bid_value")

        if value == '':
            return render(request, "auctions/approved.html", {
            "message":"Your Input was invalid. Please go back to rebid.",
            "item_id": item_id
        })
    
        bid_data = Bid(item=item, user=request.user, bid=value)
        bid_data.save()
        return render(request, "auctions/approved.html", {
            "message":"your bid was approved",
            "item_id": item_id
        })
    else:
        return index(request)
        
    
@login_required
def auction(request, auction_id, message=""):
    auction = auctions.objects.get(id=auction_id)
    comments = Comments.objects.filter(item=auction).values_list("comment", flat=True)
    bids = Bid.objects.filter(item=auction).values_list("bid", flat=True)
    try:
        watchlist = WatchList.objects.get(item=auction, user=request.user)
        button = "Remove from watchlist"
    except WatchList.DoesNotExist:
        button = "Add to Watchlist"


    if not bids:
        start_bid = auctions.objects.filter(id=auction_id).values_list("start_bid", flat=True)
        start_bid = start_bid[0]
        if start_bid < 100:
            min_bid = start_bid+5
        else:
            min_bid = start_bid+10

        bid = "The starting bid for this item is " + str(start_bid)
        return render(request, "auctions/auction.html", {
            "message":message,
            "button": button,
            "comments":comments,
            "auction":auction,
            "bid":bid,
            "min_bid": min_bid
        })
    else:
        max_bid = sorted(bids, reverse=True)
        max_bid = max_bid[0]
        if max_bid < 100:
            min_bid = max_bid+5
        else:
            min_bid = max_bid+10

        bid = "The current maximum bid for this item is " + str(max_bid) 
        return render(request, "auctions/auction.html", {
            "message":message,
            "button":button,
            "comments":comments,
            "auction":auction,
            "bid": bid,
            "min_bid": min_bid
        })

@login_required
def new_listing(request):
    if request.method == "GET":
        return render(request, "auctions/new_listing.html")
    else:
        title = request.POST.get("title").lower()
        category = request.POST.get("category").lower()
        description = request.POST.get("description")
        bid = request.POST.get("bid")
        print(request.FILES.get("picture"))
        picture = request.FILES.get("picture")


        listing = auctions(title=title.capitalize(), 
        category=category.capitalize(), 
        description=description.capitalize(), 
        start_bid=bid, 
        user=request.user, 
        status=text["active_status"],
        picture=picture)
        
        listing.save()

        return HttpResponseRedirect(reverse('index'))

  

def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "auctions/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "auctions/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "auctions/register.html", {
                "message": "Passwords must match."
            })

        try:
            email_exists = User.objects.get(email=email)
            return render(request, "auctions/register.html", {
                "message":"Error!! email already registered."
            })
        except User.DoesNotExist:
            # Attempt to create new user
            try:
                user = User.objects.create_user(username, email, password)
                user.save()
            except IntegrityError:
                return render(request, "auctions/register.html", {
                    "message": "Username already taken."
                })
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
      
            
    else:
        return render(request, "auctions/register.html")

