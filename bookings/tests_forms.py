from django.test import TestCase
from .forms import BookingForm

class TestBookingForm(TestCase):
    
    def test_date_is_required(self):
        booking_form= BookingForm({'date': ''})
        self.assertFalse(booking_form.is_valid(), msg = 'field date is valid')
    
    def test_time_is_required(self):
        booking_form= BookingForm({'time': ''})
        self.assertFalse(booking_form.is_valid(), msg = 'field time is valid')
    
    def test_guests_is_required(self):
        booking_form= BookingForm({'guests': ''})
        self.assertFalse(booking_form.is_valid(), msg = 'field guests is valid')
        
    def test_booking_form_is_valid(self):
        booking_form= BookingForm(data={'date':'2025-12-15', 'time':'19:00', 'guests':4})
        self.assertTrue(booking_form.is_valid(), msg='BookingForm is not valid')
    
    def test_guests_less_than_one_is_invalid(self):
        booking_form= BookingForm(data={'date':'2025-12-15', 'time':'19:00', 'guests':0})
        self.assertIn('guests', booking_form.errors)
        self.assertEqual(booking_form.errors['guests'][0],'Please select at least 1 guest.')
        self.assertFalse(booking_form.is_valid(), msg="This number is valid")
        
    def test_date_less_than_one_day_in_advanced_is_invalid(self):
        booking_form= BookingForm(data={'date':'2025-05-15', 'time':'19:00', 'guests':4})
        self.assertIn('date', booking_form.errors)
        self.assertEqual(booking_form.errors['date'][0],'Bookings must be made at least 1 day in advance.')
        self.assertFalse(booking_form.is_valid(), msg="This date is valid")
        
    def test_time_hours_of_business_is_invalid(self):
        booking_form= BookingForm(data={'date':'2025-05-15', 'time':'23:00', 'guests':4})
        self.assertIn('time', booking_form.errors)
        self.assertEqual(booking_form.errors['time'][0], 'Please choose a time between 11:00 am - 22:00 pm')
        self.assertFalse(booking_form.is_valid(), msg="This time is valid")
        

        