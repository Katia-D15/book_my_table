from django.test import TestCase
from django .contrib.auth.models import User
from datetime import date, time
from .models import Table, Booking, Menu


class TestModels(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username="MyUsername",
            email="test@test.com",
            password="myPassword"
        )
        self.table = Table.objects.create(number=2, seats=4)
        self.menu = Menu.objects.create(menu_name="Salmon",
                                        price=19.99
                                        )

    def test_status_default_to_pending(self):

        booking = Booking.objects.create(
            user=self.user,
            guests=4,
            date=date.today(),
            time=time(18, 0),
        )
        booking.tables.set([self.table])
        self.assertEqual(
            booking.status,
            'pending',
            msg='Default status is not pending')

    def test_table_str_method(self):
        self.assertEqual(str(self.table), "Table 2 (4 seats)")

    def test_booking_str_method(self):
        booking = Booking.objects.create(
            user=self.user,
            guests=4,
            date=date.today(),
            time=time(18, 0),
        )
        booking.tables.set([self.table])

        expected = (
            f"Booking by {self.user.username} on {booking.date} "
            f"at {booking.time} | "
            f"created at: {booking.created_at}"
        )
        self.assertEqual(str(booking), expected)

    def test_menu_str_method(self):
        self.assertEqual(str(self.menu), "Salmon - £19.99")
