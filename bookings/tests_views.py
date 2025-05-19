from django.test import TestCase
from django.contrib.auth.models import User
from django.urls import reverse
from datetime import date, time
from unittest.mock import patch
from .models import Booking, Table
from bookings.views import allocate_table


class TestViews(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(username="MyUsername",
                                             password="myPassword")
        self.client.login(username="MyUsername", password="myPassword")

        self.booking = Booking.objects.create(
            user=self.user,
            guests=4,
            date=date(2025, 12, 20),
            time=time(18, 0),
        )
        self.table1 = Table.objects.create(number=1, seats=2)
        self.table2 = Table.objects.create(number=2, seats=4)
        self.table3 = Table.objects.create(number=3, seats=6)

        self.booking.tables.add(self.table2, self.table3)

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
        response = self.client.get(reverse('my_bookings'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'bookings/my_bookings.html')

    def test_allocate_table_returns_table_if_available(self):
        result = allocate_table(date(2025, 12, 20), time(20, 0), guests=4)
        self.assertIsNotNone(result)
        self.assertEqual(result[0], self.table2)

    def test_allocate_table_returns_none_if_no_available(self):
        result = allocate_table(date(2025, 12, 20), time(18, 0), guests=4)
        self.assertIsNone(result)

    def test_allocate_table_combines_tables_if_needed(self):
        self.table2.delete()
        self.table3.delete()

        Table.objects.create(number=4, seats=2)
        Table.objects.create(number=5, seats=2)

        result = allocate_table(date(2025, 12, 22), time(20, 0), guests=4)
        self.assertIsNotNone(result)
        total_seats = sum(table.seats for table in result)
        self.assertGreaterEqual(total_seats, 4)

    def test_create_booking_user_cannot_book_same_date_and_time_twice(self):
        Booking.objects.create(
            user=self.user,
            date=date(2025, 12, 15),
            time=time(18, 0),
            guests=2)

        response = self.client.post(reverse('booking'), {
            'date': date(2025, 12, 15),
            'time': time(18, 0),
            'guests': 2}, follow=True)
        self.assertEqual(response.status_code, 200)
        messages = list(response.wsgi_request._messages)
        self.assertTrue(
            any(
                "You already have a booking that overlaps with this time."
                in m.message for m in messages))

    @patch('bookings.views.allocate_table', return_value=[])
    def test_create_booking_rejected_if_not_available_table(
        self,
        mock_allocate_table
    ):
        response = self.client.post(reverse('booking'), {
            'date': date(2025, 12, 15),
            'time': time(18, 0),
            'guests': 2}, follow=True)

        self.assertEqual(response.status_code, 200)
        mock_allocate_table.assert_called_once_with(
            date(2025, 12, 15),
            time(18, 0), 2)
        messages = list(response.wsgi_request._messages)
        self.assertTrue(
            any(
                "no tables are available for the selected time."
                in m.message for m in messages))

    def test_create_booking_successfully(self):
        response = self.client.post(reverse('booking'), {
            'date': date(2025, 12, 15),
            'time': time(18, 0),
            'guests': 2})
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('my_bookings'))
        messages = list(response.wsgi_request._messages)
        self.assertTrue(
            any("Booking made successfully!" in m.message for m in messages))

    def test_success_message_after_cancel_booking(self):
        response = self.client.get(
            reverse('cancel_booking', kwargs={'booking_id': self.booking.id})
        )
        self.assertRedirects(response, reverse('my_bookings'))
        self.booking.refresh_from_db()
        self.assertEqual(self.booking.status, 'cancelled')
        messages = list(response.wsgi_request._messages)
        self.assertTrue(
            any("Booking cancelled successfully!" in str(
                m.message) for m in messages))

    def test_warning_message_when_booking_already_cancelled(self):
        self.booking.status = 'cancelled'
        self.booking.save()
        response = self.client.get(
            reverse('cancel_booking', kwargs={'booking_id': self.booking.id})
        )
        self.assertRedirects(response, reverse('my_bookings'))

    def test_edit_guests_rejected_if_status_not_pending(self):
        self.booking.status = 'completed'
        self.booking.save()
        response = self.client.post(reverse(
            'edit_guests', kwargs={'booking_id': self.booking.id}),
                                    {'guests': 6
                                     })
        self.booking.refresh_from_db()
        self.assertNotEqual(self.booking.guests, 6)

    def test_edit_guests_rejected_if_not_one_day_in_advance(self):
        self.booking.status = 'pending'
        self.booking.date = date.today()
        self.booking.save()
        response = self.client.post(reverse(
            'edit_guests', kwargs={
                'booking_id': self.booking.id}),
                                    {'guests': 6
                                     })
        self.booking.refresh_from_db()
        self.assertNotEqual(self.booking.guests, 6)

    def test_edit_guests_rejected_if_no_tables_available(self):
        self.booking.status = 'pending'
        self.booking.date = date(2025, 12, 6)
        self.booking.save()
        with patch('bookings.views.allocate_table', return_value=None):
            response = self.client.post(reverse(
                'edit_guests', kwargs={'booking_id': self.booking.id}),
                                        {'guests': 6})
        self.booking.refresh_from_db()
        self.assertNotEqual(self.booking.guests, 6)
        messages = list(response.wsgi_request._messages)
        self.assertTrue(any(
            "There are no tables available for that number of guests."
            in m.message for m in messages))

    def test_edit_guests_updated_successfully(self):
        self.booking.status = 'pending'
        self.booking.date = date(2025, 10, 15)
        self.booking.save()
        response = self.client.post(
            reverse('edit_guests', kwargs={'booking_id': self.booking.id}),
            {'guests': 4})
        self.booking.refresh_from_db()
        self.assertEqual(self.booking.guests, 4)
        messages = list(response.wsgi_request._messages)
        self.assertTrue(any(
            "Booking updated successfully!" in m.message for m in messages
            ))
        self.assertRedirects(response, reverse('my_bookings'))

    def test_edit_guests_rejected_if_less_than_one(self):
        self.booking.status = 'pending'
        self.booking.date = date(2025, 11, 11)
        self.booking.save()
        response = self.client.post(reverse(
            'edit_guests', kwargs={'booking_id': self.booking.id}),
                                    {'guests': -6})
        self.booking.refresh_from_db()
        self.assertNotEqual(self.booking.guests, -6)
        messages = list(response.wsgi_request._messages)
        self.assertTrue(any(
            "Please select at least 1 guest" in m.message for m in messages))

    def test_edit_guests_invalid_input(self):
        self.booking.status = 'pending'
        self.booking.date = date(2025, 11, 11)
        self.booking.save()
        response = self.client.post(reverse(
            'edit_guests', kwargs={'booking_id': self.booking.id}),
                                    {'guests': 'abc'})
        self.booking.refresh_from_db()
        self.assertNotEqual(self.booking.guests, 'abc')
        messages = list(response.wsgi_request._messages)
        self.assertTrue(any(
            "Please enter a valid number of guests"
            in m.message for m in messages))
