from django.shortcuts import render
from django.views import generic
from .models import Menu, Booking

# Create your views here.
class BookMyTableList(generic.TemplateView):
    template_name = "bookings/index.html"
    
class MenuList(generic.ListView):
    queryset = Menu.objects.all()
    template_name = "bookings/menu_list.html"
    
def booking_view(request):
    """
    Present a form for the user to fill out to make a reservation
    """
    return render (request, 'bookings/booking.html')

def my_bookings(request):
    """
    Present a form for the user to fill out to make a reservation
    """
    return render (request, 'bookings/my_bookings.html')