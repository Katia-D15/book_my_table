from django.db import models
from django.contrib.auth.models import User
from cloudinary.models import CloudinaryField


# Create your models here.
class Table(models.Model):
    """
    Stores a single table, including its unique number
    and seating capacity.
    """
    number = models.PositiveIntegerField(unique=True)
    seats = models.PositiveIntegerField()

    class Meta:
        ordering = ['number']

    def __str__(self):
        return f"Table {self.number} ({self.seats} seats)"


class Booking(models.Model):
    """
    Represents a booking made by a user (:model: `auth.User`)
    for a specific date and time.
    Each booking may be linked to one or more tables (:model:`bookings.Table`)
    and includes information such as number of guests,
    status, and creation timestamp.
    """
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('cancelled', 'Cancelled'),
        ('no-show', 'No-show'),
        ('completed', 'Completed'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    guests = models.PositiveIntegerField()
    date = models.DateField()
    time = models.TimeField()
    tables = models.ManyToManyField(Table)
    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default='pending')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['date', 'time']

    def __str__(self):
        return (
            f"Booking by {self.user.username} on {self.date} at {self.time} | "
            f"created at: {self.created_at}"
        )


class Menu(models.Model):
    """
    Stores a single menu, including menus name,
    description, price and a image.
    """
    menu_name = models.CharField(max_length=100)
    description = models.TextField()
    price = models.DecimalField(max_digits=6, decimal_places=2)
    menu_image = CloudinaryField('image', default='placeholder')

    class Meta:
        ordering = ['menu_name']

    def __str__(self):
        return f"{self.menu_name} - £{self.price:.2f}"
