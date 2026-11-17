from django.db import models
from django.contrib.auth.models import User

GENDER_OPTIONS = [
    ("MALE","M"),
    ("FEMALE","F")
]

status = [('available','available'),('rented','rented'),('maintainance','maintainance')]

class Customer(models.Model):
    user = models.OneToOneField(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='customer_profile')
    name = models.CharField(max_length=30, verbose_name="customer name")
    gender = models.CharField(choices= GENDER_OPTIONS)
    telephone = models.IntegerField(null=True)
    email = models.CharField(max_length=255)

    def __str__(self):
        return f"{self.name}"

class Driver(models.Model):
    name = models.CharField(max_length=30, verbose_name="driver name")
    gender = models.CharField(choices=GENDER_OPTIONS)
    contact = models.CharField(max_length=10)
    Date_of_birth = models.DateField(verbose_name="Date of Birth")
    driver_license = models.CharField(max_length=8, null=True)
    salary = models.IntegerField()

    @property
    def date_of_birth(self):
        return self.Date_of_birth

    @date_of_birth.setter
    def date_of_birth(self, value):
        self.Date_of_birth = value

    def __str__(self):
        return f"{self.name}"

class Car(models.Model):
    car_model = models.CharField(max_length=20, null=True)
    color = models.CharField(max_length=10)
    number_plate = models.CharField(max_length=8)
    status = models.CharField(choices=status)
    rental_rate = models.IntegerField()
    image = models.ImageField(upload_to='cars/', null=True, blank=True)

    def __str__(self):
        return f"{self.car_model} of {self.color}"
    

class Service(models.Model):
    choose = [('with driver','Given a driver'),('self driving','self driving')]
    name = models.CharField(choices=choose,verbose_name="service_name")
    description = models.CharField(max_length=180)
    cost = models.IntegerField()

    def __str__(self):
        return self.name

class Hiring(models.Model):
    hiring_status = [("confirmed","confirmed"),("pending","pending")]
    customer = models.ForeignKey(Customer,on_delete=models.CASCADE)
    car = models.ForeignKey(Car,on_delete=models.CASCADE)
    service = models.ForeignKey(Service,on_delete=models.CASCADE)
    driver = models.ForeignKey(Driver,on_delete=models.SET_NULL, null=True, blank=True)
    pick_up_date = models.DateField(null=True)
    return_date = models.DateField(null=True)
    status = models.CharField(choices=hiring_status)

    def __str__(self):
        return f"{self.customer.name} hired {self.car.car_model}"

class Payment(models.Model):
    payment_status = [("completed","completed"),("pending",'pending')]
    payment_method = [("Bank","B"),("Mobile Money","MM"),("Cash","C")]
    hiring = models.ForeignKey(Hiring,on_delete=models.CASCADE)
    amount_paid = models.IntegerField()
    status = models.CharField(choices=payment_status)
    methods = models.CharField(choices=payment_method)
    payment_date = models.DateField(null=True)

    def __str__(self):
        return f"Payment of {self.amount_paid} via {self.methods} for hiring of {self.hiring.car.car_model} by {self.hiring.customer.name}"


class UserProfile(models.Model):
    ROLE_CHOICES = [('admin', 'Admin'), ('customer', 'Customer')]
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='customer')
    customer = models.OneToOneField('Customer', on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return f"{self.user.username} ({self.role})"
