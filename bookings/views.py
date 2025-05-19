from django.shortcuts import render, get_object_or_404, redirect
from django.views import generic
from django.contrib import messages
from datetime import date, timedelta, datetime
import itertools
from .models import Menu, Booking, Table
from .forms import BookingForm


# Create your views here.
class BookMyTableList(generic.TemplateView):
    """Displays the home page (index)."""
    template_name = "bookings/index.html"


class MenuList(generic.ListView):
    """Displays a list of menu items."""
    queryset = Menu.objects.all()
    template_name = "bookings/menu_list.html"


class AboutUs(generic.TemplateView):
    """Displays the About Us page."""
    template_name = "bookings/about_us.html"


class BookingPolicy(generic.TemplateView):
    """Displays the Booking Policy page."""
    template_name = "bookings/booking_policy.html"


def allocate_table(date, time, guests, exclude_booking_id=None):
    """
    Search for available tables for a booking on specific date, time
    and number of guests, avoiding conflicts with other existing bookings.

    start: date and time of booking

    end: peoriod of booking

    Returns:
    list or None: A list of tables if available, otherwise None.
    """

    start = datetime.combine(date, time)
    end = start + timedelta(hours=1)

    bookings = Booking.objects.filter(date=date)
    if exclude_booking_id:
        bookings = bookings.exclude(id=exclude_booking_id)

    unavailable_table_ids = set()
    for booking in bookings:
        start_b = datetime.combine(booking.date, booking.time)
        end_b = start_b + timedelta(hours=1)
        if start < end_b and end > start_b:
            unavailable_table_ids.update(
                booking.tables.values_list('id', flat=True))

    available_tables = (
        Table.objects.exclude(id__in=unavailable_table_ids).order_by('seats')
    )

    for num_tables in range(1, len(available_tables) + 1):
        for table_group in itertools.combinations(
            available_tables, num_tables
        ):
            total_seats = sum(table.seats for table in table_group)
            if total_seats >= guests:
                return list(table_group)

    return None


def user_has_overlapping_booking(user, date, time, exclude_booking_id=None):
    """
    It checks if the user already has a booking, that overlaps
    with the new one.
    """

    start = datetime.combine(date, time)
    end = start + timedelta(hours=1)

    bookings = Booking.objects.filter(
        user=user, date=date).exclude(status='cancelled')

    if exclude_booking_id:
        bookings = bookings.exclude(id=exclude_booking_id)

    for booking in bookings:
        start_b = datetime.combine(booking.date, booking.time)
        end_b = start_b + timedelta(hours=1)
        if start < end_b and end > start_b:
            return True

    return False


def create_booking(request):
    """
    Present a form for the user to fill out to make a booking.
    Prevents duplicate bookings for the same user at the same date/time.

    Allocates appropriate tables or shows a warning if none are available.
    """
    if request.method == "POST":
        booking_form = BookingForm(data=request.POST)
        if booking_form.is_valid():
            booking = booking_form.save(commit=False)
            booking.user = request.user

            if user_has_overlapping_booking(
                request.user, booking.date, booking.time
            ):
                messages.add_message(
                    request, messages.WARNING,
                    'You already have a booking that overlaps with this time.'
                    )
                return redirect('booking')

            tables = allocate_table(booking.date, booking.time, booking.guests)

            if not tables:
                messages.add_message(
                    request,
                    messages.WARNING,
                    'Sorry, no tables are available for the selected time.'
                    'Please try a different time or guest count.')
                return redirect('booking')

            booking.save()
            booking.tables.set(tables)
            messages.add_message(
                request,
                messages.SUCCESS,
                'Booking made successfully!')
            return redirect('my_bookings')

    else:
        booking_form = BookingForm()

    return render(
        request,
        'bookings/booking.html',
        {
            "booking_form": booking_form,
        }
        )


def my_bookings(request):
    """
    Displays a list of bookings made by the currently logged-in user.

    Returns only bookings from current day onwards, sorted by date and time.
    """
    bookings = Booking.objects.filter(user=request.user,
                                      date__gte=date.today()
                                      ).order_by('date', 'time')

    return render(
        request,
        'bookings/my_bookings.html',
        {
            'bookings': bookings,
        }
        )


def cancel_booking(request, booking_id):
    """
    Allows the current logged-in user to cancel a booking,
    as long as it hasn't already been cancelled or completed.
    """
    booking = get_object_or_404(Booking, id=booking_id, user=request.user)

    if booking.status in ('cancelled', 'completed'):
        messages.add_message(
            request, messages.WARNING,
            "This booking cannot be cancelled."
        )
        return redirect('my_bookings')

    booking.status = 'cancelled'
    booking.save()

    messages.add_message(
                request, messages.SUCCESS,
                'Booking cancelled successfully!'
            )
    return redirect('my_bookings')


def edit_guests(request, booking_id):
    """
    Allows the user to edit the number of guests for a pending
    booking, as long as it's at least 1 day berore the booking date
    and there are available tables.

    **Context**

    ``bookings``
         All bookings of the logged in user.

    ``editing_booking``
         The booking currently being edited.
    """
    booking = get_object_or_404(Booking, id=booking_id, user=request.user)
    can_edit_today = date.today() < (booking.date - timedelta(days=1))

    if request.method == 'POST':
        guests = request.POST.get('guests')

        if booking.status.lower() != 'pending':
            messages.add_message(
                request, messages.WARNING,
                'Only bookings with status "pending" can be edited.'
                )

        elif not can_edit_today:
            messages.add_message(
                request, messages.WARNING,
                'You can only edit bookings at least 1 day in advance.')

        else:
            try:
                guests = int(guests)
                if guests < 1:
                    messages.add_message(
                        request, messages.WARNING,
                        'Please select at least 1 guest.'
                    )
                else:

                    if user_has_overlapping_booking(
                        request.user, booking.date, booking.time,
                        exclude_booking_id=booking_id
                    ):
                        messages.add_message(
                            request, messages.WARNING,
                            'You already have another booking'
                            ' that overlaps with this time.'
                        )
                    else:
                        booking.guests = guests
                        tables = allocate_table(
                            booking.date,
                            booking.time,
                            booking.guests,
                            exclude_booking_id=booking.id
                            )
                    if not tables:
                        messages.add_message(
                            request, messages.WARNING,
                            'There are no tables available for that number of'
                            ' guests.'
                        )
                    else:
                        booking.save()
                        booking.tables.set(tables)
                        messages.add_message(
                            request, messages.SUCCESS,
                            'Booking updated successfully!'
                        )
                        return redirect('my_bookings')

            except ValueError:
                messages.add_message(
                    request, messages.WARNING,
                    'Please enter a valid number of guests'
                    )

    bookings = Booking.objects.filter(user=request.user,
                                      date__gte=date.today()
                                      ).order_by('date', 'time')

    return render(request, 'bookings/my_bookings.html', {
            'bookings': bookings,
            'editing_booking': booking,
        })
