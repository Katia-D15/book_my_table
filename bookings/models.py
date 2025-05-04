from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class Table(models.Model):
    """
    Stores a single table
    """
    number = models.IntegerField(unique=True)
    seats = models.IntegerField()


class Booking(models.Model):
    """
    Stores a single booking entry related to :model: `auth.User`
    and :model:`bookings.Table`
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    guests = models.IntegerField()
    date = models.DateField()
    time = models.TimeField()
    tables = models.ManyToManyField(Table)
    

class Menu(models.Model):
    """
    Stores a single menu
    """
    menu_name = models.CharField(max_length=100)
    description = models.TextField()
    price = models.DecimalField(max_digits=6, decimal_places=2)