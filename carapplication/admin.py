from django.contrib import admin
from .models import Car, Driver, Customer, Service, Hiring, Payment, UserProfile

class CustomerAdmin(admin.ModelAdmin):
    list_display = ('name', 'gender', 'telephone', 'email')

class CarAdmin(admin.ModelAdmin):
    list_display = ('car_model', 'color', 'number_plate', 'status', 'rental_rate', 'image')

class DriverAdmin(admin.ModelAdmin):
    list_display = ('name', 'gender', 'contact','Date_of_birth')

class ServiceAdmin(admin.ModelAdmin):
    list_display = ('name', 'description', 'cost')

class HiringAdmin(admin.ModelAdmin):
    list_display = ('customer', 'car', 'service', 'driver', 'status')

class PaymentAdmin(admin.ModelAdmin):
    list_display = ('hiring', 'amount_paid', 'methods', 'status')

class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'role', 'customer')

admin.site.register(Car, CarAdmin)
admin.site.register(Customer, CustomerAdmin)
admin.site.register(Driver, DriverAdmin)
admin.site.register(Service, ServiceAdmin)
admin.site.register(Hiring, HiringAdmin)
admin.site.register(Payment, PaymentAdmin)
admin.site.register(UserProfile, UserProfileAdmin)
