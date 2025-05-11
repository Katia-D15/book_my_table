from django.shortcuts import render, get_object_or_404, redirect
from django.views import generic
from django.contrib import messages
from .models import Menu, Booking
from .forms import BookingForm

# Create your views here.
class BookMyTableList(generic.TemplateView):
    template_name = "bookings/index.html"
    
class MenuList(generic.ListView):
    queryset = Menu.objects.all()
    template_name = "bookings/menu_list.html"
    
def create_booking(request):
    """
    Present a form for the user to fill out to make a reservation
    """
    if request.method == "POST":
        booking_form = BookingForm(data=request.POST)
        if booking_form.is_valid():
            booking = booking_form.save(commit = False)
            booking.user = request.user
            booking.save()
            messages.add_message(
                request, messages.SUCCESS,
                'Booking sent successfully!')
            booking_form = BookingForm()
    else:
        booking_form = BookingForm()
    
    return render (
        request,
        'bookings/booking.html',
        {
            "booking_form":booking_form,
        }
        )

def my_bookings(request):
    """
    Show a list of bookings made by the currently logged-in user.
    """
    bookings = Booking.objects.filter(user=request.user).order_by("-created_at")
    return render (
        request,
        'bookings/my_bookings.html',
        {
            'bookings': bookings,
        }
        )

def cancel_booking(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id, user=request.user)
    
    if booking.status in ('cancelled', 'completed'):
        messages.warning(request, "This booking cannot be cancelled.")
        return redirect('my_bookings')
    
    booking.status = 'cancelled'
    booking.save()
    
    messages.add_message(
                request, messages.SUCCESS,
                'Booking cancelled successfully!'
            )
    return redirect('my_bookings')

def edit_booking(request, booking_id):
    return