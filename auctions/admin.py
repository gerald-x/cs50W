from django.contrib import admin

from .models import User, auctions, WatchList, Bid, Comments

# Register your models here.
admin.site.register(User)
admin.site.register(auctions)
admin.site.register(WatchList)
admin.site.register(Bid)
admin.site.register(Comments)
