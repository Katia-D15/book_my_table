from django.contrib import admin
from django_summernote.admin import SummernoteModelAdmin
from .models import Table, Booking, Menu

@admin.register(Booking)
class BookingAdmin(SummernoteModelAdmin):
    """
    Admin interface for the Booking model.
    
    Lists fields for display in admin, fields for search,
    and fields for filters.
    """
    list_display = ('user', 'date', 'time', 'guests', 'status', 'created_at',)
    search_fields = ['user__username', 'user__first_name', 'user__last_name',]
    list_filter = ('status', 'created_at',)


@admin.register(Menu)
class MenuAdmin(SummernoteModelAdmin):
    """
    Admin interface for the Menu model.
    
    Lists menu_name and formatted price for display in admin,
    and adds rich-text editing of description in admin.
    """
    list_display = ('menu_name', 'formatted_price',)
    summernote_fields = ('description',)
    
    def formatted_price(self, obj):
        return f"£{obj.price:.2f}"
    formatted_price.short_description = 'Price'

    
@admin.register(Table)
class TableAdmin(SummernoteModelAdmin):
    """
    Admin interface for the Table model.
    
    Lists table_number and seats for display in admin,
    and enables filtering by number of seats.
    """
    list_display = ('table_number', 'seats',)
    list_filter = ('seats',)
    
    def table_number(self, obj):
        return obj.number
    
    table_number.short_description = 'Table Number'