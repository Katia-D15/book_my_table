from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class Table(models.Model):
    """
    Stores a single table
    """
    number = models.IntegerField(unique=True)
    seats = models.IntegerField()
    
    class Meta:
        ordering = ['number']
    
    def __str__(self):
        return f"Table {self.number} ({self.seats} seats)"


class Booking(models.Model):
    """
    Stores a single booking entry related to :model: `auth.User`
    and :model:`bookings.Table`
    """
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('cancelled', 'Cancelled'),
        ('no-show', 'No-show'),
        ('completed', 'Completed'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    guests = models.IntegerField()
    date = models.DateField()
    time = models.TimeField()
    tables = models.ManyToManyField(Table)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['date', 'time']
    
    def __str__(self):
        return f"Booking by {self.user.username} on {self.date} at {self.time} | created at: {self.created_at}"
    

class Menu(models.Model):
    """
    Stores a single menu
    """
    menu_name = models.CharField(max_length=100)
    description = models.TextField()
    price = models.DecimalField(max_digits=6, decimal_places=2)
    
    class Meta:
        ordering = ['menu_name']
    
    def __str__(self):
        return f"{self.menu_name} - £{self.price:.2f}"