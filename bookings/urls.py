from . import views
from django.urls import path

urlpatterns = [
    path('', views.BookMyTableList.as_view(), name='home'),
    path('booking/', views.booking_view, name='booking'),
    path('menu/', views.MenuList.as_view(), name='menu'),
    path('my-bookings/', views.my_bookings, name='my_bookings'),
]
