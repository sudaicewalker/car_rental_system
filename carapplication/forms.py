from django.forms import ModelForm
from django import forms
from django.contrib.auth.models import User
from .models import Car, Customer, Hiring, Service, Payment, Driver


class CustomerForm(ModelForm):
    class Meta:
        model = Customer
        fields = '__all__'

class DriverForm(ModelForm):
    class Meta:
        model = Driver
        fields = '__all__'
        widgets = {
            'Date_of_birth': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
        }

class CarForm(ModelForm):
    class Meta:
        model = Car
        fields = '__all__'

class ServiceForm(ModelForm):
    class Meta:
        model = Service
        fields = '__all__'

class HiringForm(ModelForm):
    class Meta:
        model = Hiring
        fields = '__all__'

class PaymentForm(ModelForm):
    class Meta:
        model = Payment
        fields = '__all__'


class SignupForm(forms.Form):
    username = forms.CharField(
        max_length=150,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Choose a username'})
    )
    first_name = forms.CharField(
        max_length=30,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'First name'})
    )
    last_name = forms.CharField(
        max_length=30,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Last name'})
    )
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Email address'})
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Create password'})
    )
    confirm_password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Confirm password'})
    )

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError("This username is already taken.")
        return username

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        confirm = cleaned_data.get('confirm_password')
        if password and confirm and password != confirm:
            raise forms.ValidationError("Passwords do not match.")
        return cleaned_data


class CustomerBookingForm(forms.ModelForm):
    class Meta:
        model = Hiring
        fields = ['car', 'service', 'pick_up_date', 'return_date']
        widgets = {
            'car': forms.Select(attrs={'class': 'form-select'}),
            'service': forms.Select(attrs={'class': 'form-select'}),
            'pick_up_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'return_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['car'].queryset = Car.objects.filter(status='available')


class CustomerPaymentForm(forms.ModelForm):
    class Meta:
        model = Payment
        fields = ['amount_paid', 'methods', 'payment_date']
        widgets = {
            'amount_paid': forms.NumberInput(attrs={'class': 'form-control'}),
            'methods': forms.Select(attrs={'class': 'form-select'}),
            'payment_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        }


class CarStatusForm(forms.ModelForm):
    class Meta:
        model = Car
        fields = ['status']
        widgets = {
            'status': forms.Select(attrs={'class': 'form-select'}),
        }


class AssignDriverForm(forms.ModelForm):
    class Meta:
        model = Hiring
        fields = ['driver']
        widgets = {
            'driver': forms.Select(attrs={'class': 'form-select'}),
        }
