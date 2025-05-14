from django import forms
from django.utils import timezone
from datetime import time
from .models import Booking

class BookingForm(forms.ModelForm):
    """
    Form class for user make a booking
    """
    class Meta:
        """
        Specify the django model and order the fields
        """
        model = Booking
        fields = ('date', 'time', 'guests',)
        labels = {
            'date': 'Choose a date for your Booking',
            'time': 'Choose a time between 11:00 am - 22:00 pm',
            'guests': 'Total number of people (including yourself)',
        }
        
        widgets = {
            'date': forms.DateInput(attrs={
                'type': 'date',
                'class': 'form-control',
            }),
            'time': forms.TimeInput(attrs={
                'type': 'time',
                'class': 'form-control',
            }),
            'guests': forms.NumberInput(attrs={
                'type': 'number',
                'min': 1,
                'class': 'form-control',
            }),
        }
    
    def clean_guests(self):
        """
        Restrict the number of guests, or 1 or more.
        """
        guests = self.cleaned_data.get('guests')
        if guests < 1:
            raise forms.ValidationError("Please select at least 1 guest.")
        return guests


    def clean_date(self):
        """
        Ensures that the booking date is not a past date,
        but at least one day in advance.
        """
        date = self.cleaned_data.get('date')
        today = timezone.localdate()
        if date <= today:
            raise forms.ValidationError("Bookings must be made at least 1 day in advance.")
        return date
    

    def clean_time(self):
        """
        Ensure that the selected time respects the business hours.
        """
        selected_time = self.cleaned_data.get('time')
        
        if not selected_time:
            return selected_time
        
        opening_time = time(11,0)
        last_booking_time = time(22,0)
        
        if selected_time < opening_time or selected_time > last_booking_time:
            raise forms.ValidationError("Please choose a time between 11:00 am - 22:00 pm")
        return selected_time