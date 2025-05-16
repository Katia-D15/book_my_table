from django.test import TestCase
from django .contrib.auth.models import User
from django.urls import reverse
from datetime import date, time
from unittest.mock import patch
from .models import Booking, Table

class TestViews(TestCase):
    
    def setUp(self):
        self.user = User.objects.create_user(username="MyUsername",
                                             password= "myPassword")
        self.booking= Booking.objects.create(
            user= self.user,
            guests= 4,
            date= date.today(),
            time= time(18,0),
        )
        table = Table.objects.create(number= 2, seats= 4)
        self.booking.tables.add(table)
        
    
    def test_get_home_page(self):
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'bookings/index.html')
    
    def test_get_about_us_page(self):
        response = self.client.get(reverse('about_us'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'bookings/about_us.html')
    
    def test_get_booking_page(self):
        response = self.client.get(reverse('booking'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'bookings/booking.html')
    
    def test_get_booking_policy_page(self):
        response = self.client.get(reverse('booking_policy'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'bookings/booking_policy.html')
        
    
    def test_get_menu_list_page(self):
        response = self.client.get(reverse('menu'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'bookings/menu_list.html')
    
    def test_logged_in_user_can_my_bookings_page(self):
        self.client.login(username= "MyUsername",password= "myPassword")
        response = self.client.get(reverse('my_bookings'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'bookings/my_bookings.html')

    def test_edit_guests_rejected_if_status_not_pending(self):
        self.client.login(username= "MyUsername",password= "myPassword")
        self.booking.status = 'completed'
        self.booking.save()
        response = self.client.post(reverse('edit_guests', kwargs={'booking_id': self.booking.id}),
                                    {'guests':6
                                     })
        self.booking.refresh_from_db()
        self.assertNotEqual(self.booking.guests, 6)
    
    def test_edit_guests_rejected_if_not_one_day_in_advance(self):
        self.client.login(username= "MyUsername",password= "myPassword")
        self.booking.status = 'pending'
        self.booking.date = date.today()
        self.booking.save()
        response = self.client.post(reverse('edit_guests', kwargs={'booking_id': self.booking.id}),
                                    {'guests':6
                                     })
        self.booking.refresh_from_db()
        self.assertNotEqual(self.booking.guests, 6)
            
    def test_edit_guests_rejected_if_no_tables_available(self):
        self.client.login(username= "MyUsername",password= "myPassword")
        self.booking.status = 'pending'
        self.booking.date = date(2025,12,6)
        self.booking.save()
        with patch('bookings.views.allocate_table', return_value=None):
            response = self.client.post(reverse('edit_guests', kwargs={'booking_id': self.booking.id}),
                                    {'guests':6
                                     })
        self.booking.refresh_from_db()
        self.assertNotEqual(self.booking.guests, 6)
        messages = list(response.wsgi_request._messages)
        self.assertTrue(any("There are no tables available for that number of guests." in m.message for m in messages))

            
    
    def test_edit_guests_updated_successfully(self):
        self.client.login(username= "MyUsername",password= "myPassword")
        self.booking.status = 'pending'
        self.booking.date = date(2025,10,15)
        self.booking.save()
        response = self.client.post(reverse('edit_guests', kwargs={'booking_id': self.booking.id}),
                                    {'guests':4
                                     })
        self.booking.refresh_from_db()
        self.assertEqual(self.booking.guests, 4)
        messages = list(response.wsgi_request._messages)
        self.assertTrue(any("Booking updated successfully!" in m.message for m in messages))
        self.assertRedirects(response, reverse('my_bookings'))
            
            
    def test_edit_guests_rejected_if_less_than_one(self):
        self.client.login(username= "MyUsername",password= "myPassword")
        self.booking.status = 'pending'
        self.booking.date = date(2025,11,11)
        self.booking.save()
        response = self.client.post(reverse('edit_guests', kwargs={'booking_id': self.booking.id}),
                                    {'guests':-6
                                     })
        self.booking.refresh_from_db()
        self.assertNotEqual(self.booking.guests, -6)
        messages = list(response.wsgi_request._messages)
        self.assertTrue(any(
            "Please select at least 1 guest" in m.message for m in messages))
        
    def test_edit_guests_invalid_input(self):
        self.client.login(username= "MyUsername",password= "myPassword")
        self.booking.status = 'pending'
        self.booking.date = date(2025,11,11)
        self.booking.save()
        response = self.client.post(reverse('edit_guests', kwargs={'booking_id': self.booking.id}),
                                    {'guests':'abc'
                                     })
        self.booking.refresh_from_db()
        self.assertNotEqual(self.booking.guests, 'abc')
        messages = list(response.wsgi_request._messages)
        self.assertTrue(any(
            "Please enter a valid number of guests" in m.message for m in messages))
