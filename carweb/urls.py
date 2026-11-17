"""
URL configuration for carweb project.
"""
from django.contrib import admin
from django.urls import path, re_path
from django.conf import settings
from django.conf.urls.static import static
from django.views.static import serve

from carapplication.views import (
    index_view, next_page_view, base_view,
    add_customer_view, add_driver_view, add_car_view, add_service_view,
    add_hiring_view, add_payment_view,
    edit_customer_view, edit_driver_view, edit_car_view, edit_service_view,
    edit_hiring_view, edit_payment_view,
    delete_service_view, delete_cutomer_view, delete_driver_view,
    delete_car_view, delete_hiring_view, delete_payment_view,
    signup_view, login_view, logout_view,
    customer_dashboard_view, customer_book_view, my_bookings_view, customer_pay_view,
    change_car_status_view, assign_driver_view, admin_analytics_view,
)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', index_view, name='index_page'),
    path('next/', next_page_view, name='next_page'),
    path('base/', base_view, name='base_page'),

    # Auth
    path('signup/', signup_view, name='signup_page'),
    path('login/', login_view, name='login_page'),
    path('logout/', logout_view, name='logout_page'),

    # Admin CRUD
    path("add_customer/", add_customer_view, name="add_customer"),
    path("add_driver/", add_driver_view, name="add_driver"),
    path("add_car/", add_car_view, name="add_car"),
    path("add_service/", add_service_view, name="add_service"),
    path("add_hiring/", add_hiring_view, name="add_hiring"),
    path("add_payment/", add_payment_view, name="add_payment"),
    path("edit_customer/<int:customer_id>/", edit_customer_view, name="edit_customer"),
    path("edit_driver/<int:driver_id>/", edit_driver_view, name="edit_driver"),
    path("edit_car/<int:car_id>/", edit_car_view, name="edit_car"),
    path("edit_service/<int:service_id>/", edit_service_view, name="edit_service"),
    path("edit_hiring/<int:hire_id>/", edit_hiring_view, name="edit_hiring"),
    path("edit_payment/<int:payment_id>/", edit_payment_view, name="edit_payment"),
    path("delete_service/<int:service_id>/", delete_service_view, name="delete_service"),
    path("delete_customer/<int:customer_id>/", delete_cutomer_view, name="delete_customer"),
    path("delete_driver/<int:driver_id>/", delete_driver_view, name="delete_driver"),
    path("delete_car/<int:car_id>/", delete_car_view, name="delete_car"),
    path("delete_hiring/<int:hire_id>/", delete_hiring_view, name="delete_hiring"),
    path("delete_payment/<int:payment_id>/", delete_payment_view, name="delete_payment"),

    # Customer portal
    path('customer/dashboard/', customer_dashboard_view, name='customer_dashboard'),
    path('customer/book/', customer_book_view, name='customer_book'),
    path('customer/my_bookings/', my_bookings_view, name='my_bookings'),
    path('customer/pay/<int:hiring_id>/', customer_pay_view, name='customer_pay'),

    # Admin panel extras & analytics
    path('admin_panel/change_car_status/<int:car_id>/', change_car_status_view, name='change_car_status'),
    path('admin_panel/assign_driver/<int:hire_id>/', assign_driver_view, name='assign_driver'),
    path('admin_panel/analytics/', admin_analytics_view, name='admin_analytics'),
]

# Serve media files in both development and production
urlpatterns += [
    re_path(r'^media/(?P<path>.*)$', serve, {'document_root': settings.MEDIA_ROOT}),
]
