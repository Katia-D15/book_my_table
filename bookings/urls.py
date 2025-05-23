from django.urls import path
from . import views

urlpatterns = [
    path('', views.BookMyTableList.as_view(), name='home'),
    path('booking/', views.create_booking, name='booking'),
    path('menu/', views.MenuList.as_view(), name='menu'),
    path('my-bookings/', views.my_bookings, name='my_bookings'),
    path('cancel-booking/<int:booking_id>/',
         views.cancel_booking, name='cancel_booking'),
    path('edit-guests/<int:booking_id>/', views.edit_guests,
         name='edit_guests'),
    path('about-us/', views.AboutUs.as_view(), name='about_us'),
    path('booking_policy/', views.BookingPolicy.as_view(),
         name='booking_policy'),
]
