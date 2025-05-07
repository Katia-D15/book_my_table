from django.shortcuts import render
from django.views import generic
from .models import Menu, Booking

# Create your views here.
class BookMyTableList(generic.TemplateView):
    template_name = "bookings/index.html"
    
class MenuList(generic.ListView):
    queryset = Menu.objects.all()
    template_name = "bookings/menu_list.html"