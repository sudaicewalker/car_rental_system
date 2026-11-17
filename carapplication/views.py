from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.db.models import Sum, Count, Value
from django.db.models.functions import Coalesce
from functools import wraps

from .forms import (
    CustomerForm, DriverForm, CarForm, ServiceForm, HiringForm, PaymentForm,
    SignupForm, CustomerBookingForm, CustomerPaymentForm, CarStatusForm, AssignDriverForm
)
from .models import Customer, Car, Driver, Service, Hiring, Payment, UserProfile


# ---------------------------------------------------------------------------
# Decorators
# ---------------------------------------------------------------------------

def admin_required(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('login_page')
        is_admin = (
            request.user.is_superuser or
            request.user.is_staff or
            (hasattr(request.user, 'profile') and request.user.profile.role == 'admin')
        )
        if not is_admin:
            return redirect('customer_dashboard')
        return view_func(request, *args, **kwargs)
    return _wrapped_view


def customer_required(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('login_page')
        if not hasattr(request.user, 'profile') or request.user.profile.role != 'customer':
            return redirect('index_page')
        return view_func(request, *args, **kwargs)
    return _wrapped_view


# ---------------------------------------------------------------------------
# Auth Views
# ---------------------------------------------------------------------------

def signup_view(request):
    form = SignupForm()
    error = ''
    if request.method == 'POST':
        form = SignupForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            user = User.objects.create_user(
                username=data['username'],
                password=data['password'],
                first_name=data['first_name'],
                last_name=data['last_name'],
                email=data['email'],
            )
            # Create linked Customer record
            customer = Customer.objects.create(
                user=user,
                name=f"{data['first_name']} {data['last_name']}",
                gender='MALE',  # default; admin can update later
                telephone=0,
                email=data['email'],
            )
            # Create UserProfile with role='customer'
            UserProfile.objects.create(user=user, role='customer', customer=customer)
            return redirect('login_page')
        else:
            error = 'Please correct the errors below.'
    return render(request, 'signup.html', {'form': form, 'error': error})


def login_view(request):
    error = ''
    if request.user.is_authenticated:
        if hasattr(request.user, 'profile') and request.user.profile.role == 'admin':
            return redirect('index_page')
        return redirect('customer_dashboard')

    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            # Ensure profile exists
            if not hasattr(user, 'profile'):
                default_role = 'admin' if (user.is_staff or user.is_superuser) else 'customer'
                UserProfile.objects.create(user=user, role=default_role)
            if user.profile.role == 'admin' or user.is_staff or user.is_superuser:
                return redirect('index_page')
            return redirect('customer_dashboard')
        else:
            error = 'Invalid username or password. Please try again.'
    return render(request, 'login_page.html', {'error': error})


def logout_view(request):
    logout(request)
    return redirect('login_page')


def get_customer_for_user(user):
    try:
        if hasattr(user, 'customer_profile') and user.customer_profile:
            return user.customer_profile
    except Exception:
        pass
    if hasattr(user, 'profile') and user.profile.customer:
        return user.profile.customer
    customer = Customer.objects.filter(user=user).first()
    if customer:
        return customer
    customer, _ = Customer.objects.get_or_create(
        user=user,
        defaults={
            'name': user.get_full_name() or user.username,
            'gender': 'MALE',
            'telephone': 0,
            'email': user.email or f"{user.username}@example.com"
        }
    )
    if hasattr(user, 'profile') and not user.profile.customer:
        user.profile.customer = customer
        user.profile.save()
    return customer


# ---------------------------------------------------------------------------
# Public / General Views
# ---------------------------------------------------------------------------

def index_view(request):
    total_cars = Car.objects.count()
    rented_cars = Car.objects.filter(status='rented').count()
    available_cars = Car.objects.filter(status='available').count()
    drivers_count = Driver.objects.count()
    cars = Car.objects.all()
    services = Service.objects.all()

    # Revenue & Analytics
    overall_revenue = Payment.objects.filter(status='completed').aggregate(
        total=Coalesce(Sum('amount_paid'), Value(0))
    )['total']
    total_revenue_all = Payment.objects.aggregate(
        total=Coalesce(Sum('amount_paid'), Value(0))
    )['total']
    pending_revenue = Payment.objects.filter(status='pending').aggregate(
        total=Coalesce(Sum('amount_paid'), Value(0))
    )['total']

    # Which car is rented many times
    cars_by_rentals = Car.objects.annotate(
        rental_count=Count('hiring', distinct=True),
        total_revenue=Coalesce(Sum('hiring__payment__amount_paid'), Value(0))
    ).order_by('-rental_count', '-total_revenue')
    most_rented_car = cars_by_rentals.first()

    # Revenue by each customer
    customers_revenue = Customer.objects.annotate(
        bookings_count=Count('hiring', distinct=True),
        total_spent=Coalesce(Sum('hiring__payment__amount_paid'), Value(0))
    ).order_by('-total_spent', '-bookings_count')

    context = {
        'total_cars': total_cars,
        'rented_cars': rented_cars,
        'available_cars': available_cars,
        'drivers_count': drivers_count,
        'cars': cars,
        'services': services,
        'overall_revenue': overall_revenue,
        'total_revenue_all': total_revenue_all,
        'pending_revenue': pending_revenue,
        'cars_by_rentals': cars_by_rentals,
        'most_rented_car': most_rented_car,
        'customers_revenue': customers_revenue,
    }
    return render(request, 'index.html', context)


def base_view(request):
    return render(request, 'base.html')


def next_page_view(request):
    return render(request, 'next_page.html')


# ---------------------------------------------------------------------------
# Admin-only Views — CRUD
# ---------------------------------------------------------------------------

@admin_required
def add_customer_view(request):
    message = ''
    if request.method == "POST":
        customer_form = CustomerForm(request.POST)
        if customer_form.is_valid():
            customer_form.save()
            message = 'customer added successfully'
    else:
        customer_form = CustomerForm()

    customers = Customer.objects.all()
    context = {
        'form': customer_form,
        'msg': message,
        'customers': customers
    }
    return render(request, "add_customer.html", context)


@admin_required
def add_driver_view(request):
    message = ''
    if request.method == "POST":
        post_data = request.POST.copy()
        if 'date_of_birth' in post_data and 'Date_of_birth' not in post_data:
            post_data['Date_of_birth'] = post_data['date_of_birth']
        driver_form = DriverForm(post_data)
        if driver_form.is_valid():
            driver_form.save()
            message = 'Driver added successfully'
    else:
        driver_form = DriverForm()

    drivers = Driver.objects.all()
    context = {
        "form": driver_form,
        "msg": message,
        "drivers": drivers
    }
    return render(request, "add_driver.html", context)


@admin_required
def add_car_view(request):
    message = ''
    if request.method == "POST":
        car_form = CarForm(request.POST, request.FILES)
        if car_form.is_valid():
            car_form.save()
            message = 'car added successfully'
    else:
        car_form = CarForm()

    cars = Car.objects.all()
    context = {
        "form": car_form,
        "msg": message,
        "cars": cars
    }
    return render(request, "add_car.html", context)


@admin_required
def add_service_view(request):
    message = ''
    if request.method == "POST":
        servive_form = ServiceForm(request.POST)
        if servive_form.is_valid():
            servive_form.save()
            message = "Service has been added"
    else:
        servive_form = ServiceForm()

    services = Service.objects.all()
    context = {
        "form": servive_form,
        "msg": message,
        "services": services
    }
    return render(request, "add_service.html", context)


@admin_required
def add_hiring_view(request):
    message = ''
    if request.method == "POST":
        hiring_form = HiringForm(request.POST)
        if hiring_form.is_valid():
            hiring_form.save()
            message = 'Record added successfully'
    else:
        hiring_form = HiringForm()

    hires = Hiring.objects.all()
    customers = Customer.objects.all()
    cars = Car.objects.all()
    services = Service.objects.all()
    drivers = Driver.objects.all()
    context = {
        "form": hiring_form,
        "msg": message,
        "hires": hires,
        "customers": customers,
        "cars": cars,
        "services": services,
        "drivers": drivers,
    }
    return render(request, "add_hiring.html", context)


@admin_required
def add_payment_view(request):
    message = ''
    if request.method == "POST":
        payment_form = PaymentForm(request.POST)
        if payment_form.is_valid():
            payment_form.save()
            message = 'payment is successfully'
    else:
        payment_form = PaymentForm()

    payments = Payment.objects.all()
    hires = Hiring.objects.all()
    context = {
        "form": payment_form,
        "msg": message,
        "payments": payments,
        "hires": hires,
    }
    return render(request, "add_payment.html", context)


@admin_required
def edit_customer_view(request, customer_id):
    message = ''
    customer = get_object_or_404(Customer, id=customer_id)
    if request.method == "POST":
        customer_form = CustomerForm(request.POST, instance=customer)
        if customer_form.is_valid():
            customer_form.save()
            return redirect(request.META.get('HTTP_REFERER') or 'add_customer')
        else:
            message = 'Form has invalid data'
    else:
        customer_form = CustomerForm(instance=customer)

    context = {
        "form": customer_form,
        "customer": customer,
        "msg": message
    }
    return render(request, "edit_customer.html", context)


@admin_required
def edit_driver_view(request, driver_id):
    message = ''
    driver = get_object_or_404(Driver, id=driver_id)
    if request.method == "POST":
        post_data = request.POST.copy()
        if 'date_of_birth' in post_data and 'Date_of_birth' not in post_data:
            post_data['Date_of_birth'] = post_data['date_of_birth']
        driver_form = DriverForm(post_data, instance=driver)
        if driver_form.is_valid():
            driver_form.save()
            return redirect(request.META.get('HTTP_REFERER') or 'add_driver')
        else:
            message = 'form has invalid data'
    else:
        driver_form = DriverForm(instance=driver)

    context = {
        "form": driver_form,
        "msg": message,
        "driver": driver
    }
    return render(request, "edit_driver.html", context)


@admin_required
def edit_car_view(request, car_id):
    message = ''
    car = get_object_or_404(Car, id=car_id)
    if request.method == "POST":
        car_form = CarForm(request.POST, request.FILES, instance=car)
        if car_form.is_valid():
            car_form.save()
            return redirect(request.META.get('HTTP_REFERER') or 'add_car')
        else:
            message = 'form has invalid data'
    else:
        car_form = CarForm(instance=car)

    context = {
        "form": car_form,
        "msg": message,
        "car": car
    }
    return render(request, "edit_car.html", context)


@admin_required
def edit_service_view(request, service_id):
    message = ''
    service = get_object_or_404(Service, id=service_id)
    if request.method == "POST":
        service_form = ServiceForm(request.POST, instance=service)
        if service_form.is_valid():
            service_form.save()
            return redirect(request.META.get('HTTP_REFERER') or 'add_service')
        else:
            message = 'form has invalid data'
    else:
        service_form = ServiceForm(instance=service)

    context = {
        "form": service_form,
        "msg": message,
        "service": service
    }
    return render(request, "edit_service.html", context)


@admin_required
def edit_hiring_view(request, hire_id):
    message = ''
    hiring = get_object_or_404(Hiring, id=hire_id)
    if request.method == "POST":
        hiring_form = HiringForm(request.POST, instance=hiring)
        if hiring_form.is_valid():
            hiring_form.save()
            return redirect(request.META.get('HTTP_REFERER') or 'add_hiring')
        else:
            message = 'form has invalid data'
    else:
        hiring_form = HiringForm(instance=hiring)

    context = {
        "form": hiring_form,
        "msg": message,
        "hiring": hiring
    }
    return render(request, "edit_hiring.html", context)


@admin_required
def edit_payment_view(request, payment_id):
    message = ''
    payment = get_object_or_404(Payment, id=payment_id)
    if request.method == "POST":
        payment_form = PaymentForm(request.POST, instance=payment)
        if payment_form.is_valid():
            payment_form.save()
            return redirect(request.META.get('HTTP_REFERER') or 'add_payment')
        else:
            message = 'form has invalid data'
    else:
        payment_form = PaymentForm(instance=payment)

    context = {
        "form": payment_form,
        "msg": message,
        "payment": payment
    }
    return render(request, "edit_payment.html", context)


@admin_required
def delete_service_view(request, service_id):
    service = get_object_or_404(Service, id=service_id)
    service.delete()
    return redirect(request.META.get('HTTP_REFERER') or 'add_service')


@admin_required
def delete_cutomer_view(request, customer_id):
    customer = get_object_or_404(Customer, id=customer_id)
    customer.delete()
    return redirect(request.META.get('HTTP_REFERER') or 'add_customer')


@admin_required
def delete_driver_view(request, driver_id):
    driver = get_object_or_404(Driver, id=driver_id)
    driver.delete()
    return redirect(request.META.get('HTTP_REFERER') or 'add_driver')


@admin_required
def delete_car_view(request, car_id):
    car = get_object_or_404(Car, id=car_id)
    car.delete()
    return redirect(request.META.get('HTTP_REFERER') or 'add_car')


@admin_required
def delete_hiring_view(request, hire_id):
    hiring = get_object_or_404(Hiring, id=hire_id)
    hiring.delete()
    return redirect(request.META.get('HTTP_REFERER') or 'add_hiring')


@admin_required
def delete_payment_view(request, payment_id):
    payment = get_object_or_404(Payment, id=payment_id)
    payment.delete()
    return redirect(request.META.get('HTTP_REFERER') or 'add_payment')


# ---------------------------------------------------------------------------
# Admin Panel — Car Status & Driver Assignment
# ---------------------------------------------------------------------------

@admin_required
def change_car_status_view(request, car_id):
    car = get_object_or_404(Car, id=car_id)
    message = ''
    if request.method == 'POST':
        form = CarStatusForm(request.POST, instance=car)
        if form.is_valid():
            form.save()
            message = 'Car status updated successfully.'
            return redirect(request.META.get('HTTP_REFERER') or 'add_car')
    else:
        form = CarStatusForm(instance=car)
    return render(request, 'change_car_status.html', {'car': car, 'form': form, 'msg': message})


@admin_required
def assign_driver_view(request, hire_id):
    hiring = get_object_or_404(Hiring, id=hire_id)
    message = ''
    if request.method == 'POST':
        form = AssignDriverForm(request.POST, instance=hiring)
        if form.is_valid():
            form.save()
            message = 'Driver assigned successfully.'
            return redirect(request.META.get('HTTP_REFERER') or 'add_hiring')
    else:
        form = AssignDriverForm(instance=hiring)
    return render(request, 'assign_driver.html', {'hiring': hiring, 'form': form, 'msg': message})


@admin_required
def admin_analytics_view(request):
    completed_revenue = Payment.objects.filter(status='completed').aggregate(
        total=Coalesce(Sum('amount_paid'), Value(0))
    )['total']
    pending_revenue = Payment.objects.filter(status='pending').aggregate(
        total=Coalesce(Sum('amount_paid'), Value(0))
    )['total']
    total_revenue = Payment.objects.aggregate(
        total=Coalesce(Sum('amount_paid'), Value(0))
    )['total']

    total_hirings = Hiring.objects.count()
    confirmed_hirings = Hiring.objects.filter(status='confirmed').count()
    pending_hirings = Hiring.objects.filter(status='pending').count()

    # Which car is rented many times
    cars_by_rentals = Car.objects.annotate(
        rental_count=Count('hiring', distinct=True),
        total_revenue=Coalesce(Sum('hiring__payment__amount_paid'), Value(0))
    ).order_by('-rental_count', '-total_revenue')
    most_rented_car = cars_by_rentals.first()

    # Revenue by each customer
    customers_revenue = Customer.objects.annotate(
        bookings_count=Count('hiring', distinct=True),
        total_spent=Coalesce(Sum('hiring__payment__amount_paid'), Value(0))
    ).order_by('-total_spent', '-bookings_count')

    context = {
        'completed_revenue': completed_revenue,
        'pending_revenue': pending_revenue,
        'total_revenue': total_revenue,
        'total_hirings': total_hirings,
        'confirmed_hirings': confirmed_hirings,
        'pending_hirings': pending_hirings,
        'cars_by_rentals': cars_by_rentals,
        'most_rented_car': most_rented_car,
        'customers_revenue': customers_revenue,
    }
    return render(request, 'admin_analytics.html', context)


# ---------------------------------------------------------------------------
# Customer Views
# ---------------------------------------------------------------------------

@customer_required
def customer_dashboard_view(request):
    customer = get_customer_for_user(request.user)
    bookings = Hiring.objects.filter(customer=customer) if customer else Hiring.objects.none()
    total_bookings = bookings.count()
    pending_bookings = bookings.filter(status='pending').count()

    paid_hirings = bookings.values_list('id', flat=True)
    completed_payments = Payment.objects.filter(hiring_id__in=paid_hirings, status='completed').count()

    recent_bookings = bookings.order_by('-id')[:5]

    context = {
        'customer': customer,
        'total_bookings': total_bookings,
        'pending_bookings': pending_bookings,
        'completed_payments': completed_payments,
        'recent_bookings': recent_bookings,
    }
    return render(request, 'customer_dashboard.html', context)


@customer_required
def customer_book_view(request):
    customer = get_customer_for_user(request.user)

    message = ''
    error = ''
    available_cars = Car.objects.filter(status='available')
    services = Service.objects.all()

    if request.method == 'POST':
        form = CustomerBookingForm(request.POST)
        if form.is_valid():
            hiring = form.save(commit=False)
            hiring.customer = customer
            hiring.driver = None
            hiring.status = 'pending'
            hiring.save()
            # Update car status to rented
            car = hiring.car
            car.status = 'rented'
            car.save()
            return redirect('customer_dashboard')
        else:
            error = 'Please correct the form errors.'
    else:
        form = CustomerBookingForm()

    context = {
        'form': form,
        'available_cars': available_cars,
        'services': services,
        'msg': message,
        'error': error,
    }
    return render(request, 'customer_book.html', context)


@customer_required
def my_bookings_view(request):
    customer = get_customer_for_user(request.user)
    bookings = Hiring.objects.filter(customer=customer).order_by('-id') if customer else Hiring.objects.none()

    # Annotate with payment info
    bookings_data = []
    for b in bookings:
        payments = Payment.objects.filter(hiring=b)
        has_payment = payments.exists()
        payment_status = payments.first().status if has_payment else 'No Payment'
        bookings_data.append({
            'booking': b,
            'has_payment': has_payment,
            'payment_status': payment_status,
        })

    context = {
        'bookings_data': bookings_data,
    }
    return render(request, 'my_bookings.html', context)


@customer_required
def customer_pay_view(request, hiring_id):
    hiring = get_object_or_404(Hiring, id=hiring_id)

    # Ensure this booking belongs to the logged-in customer
    customer = get_customer_for_user(request.user)
    if hiring.customer != customer:
        return redirect('my_bookings')

    # Calculate total
    total_amount = 0
    if hiring.pick_up_date and hiring.return_date:
        delta = (hiring.return_date - hiring.pick_up_date).days
        if delta > 0:
            total_amount = delta * hiring.car.rental_rate

    message = ''
    if request.method == 'POST':
        form = CustomerPaymentForm(request.POST)
        if form.is_valid():
            payment = form.save(commit=False)
            payment.hiring = hiring
            payment.status = 'pending'
            payment.save()
            return redirect('my_bookings')
    else:
        form = CustomerPaymentForm(initial={'amount_paid': total_amount})

    context = {
        'hiring': hiring,
        'total_amount': total_amount,
        'form': form,
        'msg': message,
    }
    return render(request, 'customer_pay.html', context)
