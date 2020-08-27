from django.contrib import admin
from .models import Order, OrderItem, Item, Address, Payment, Donor 

class ItemAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('title', )}
    list_display = [
        'title',
        'price',
        'discount_price'
    ]

class AddressAdmin(admin.ModelAdmin):
    list_display = [
        'street_address',
        'apartment_address',
        'country',
        'zip',
        'default'
    ]


class DonorAdmin(admin.ModelAdmin):
    list_display = [
        'name',
        'age',
        'blood_group',
        'phone',
        'address'
    ]

class OrderAdmin(admin.ModelAdmin):
    list_display = [
        'user',
       
        'address',
        'payment',
        'ordered',
        'start_date',
        'ordered_date'
    ]
class OrderItemAdmin(admin.ModelAdmin):
    list_display = [
        'user',
        'item',
        'ordered',
        'quantity',
        
    ]



admin.site.register(Donor, DonorAdmin)
admin.site.register(Payment)
admin.site.register(Address, AddressAdmin)
admin.site.register(Item, ItemAdmin)
admin.site.register(Order, OrderAdmin)
admin.site.register(OrderItem, OrderItemAdmin)