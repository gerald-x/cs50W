from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models.aggregates import Min


class User(AbstractUser):
    pass

class auctions(models.Model):
    title = models.CharField(max_length=80)
    picture = models.ImageField(upload_to="images/")
    category = models.CharField(max_length=60)
    description = models.TextField()
    start_bid = models.PositiveIntegerField()
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    status = models.CharField(max_length=10, default="active")

    
class WatchList(models.Model):
    item = models.ForeignKey(auctions, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

class Bid(models.Model):
    item = models.ForeignKey(auctions, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    bid = models.PositiveIntegerField()

class Comments(models.Model):
    comment = models.TextField()
    user = models.ForeignKey(User, on_delete=models.PROTECT)
    item = models.ForeignKey(auctions, on_delete=models.CASCADE)