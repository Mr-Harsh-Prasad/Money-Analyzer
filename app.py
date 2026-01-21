#!/usr/bin/env python
# core/models.py
from django.db import models
from django.contrib.auth.models import user
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import Transaction, Category, SavingsGoal, Budget
from django.contrib.auth.forms import TransactionForm, RegisterForm, CategoryForm, SavingsGoalForm
from django.db.models import Sum
from datetime import date
from django import forms, views
from django.contrib.auth.models import Entry, Category, SavingsGoal
from django.contrib.auth.forms import UserCreationForm
from django.apps import AppConfig
from django.urls import path
from django.contrib import admin

class Category(models.TextChoices):

   FOOD = 'food', 'Food'
   TRANSPORT = 'transport', 'Transport'
   BILLS = 'bills', 'Bills' 
   ENTERTAINMENT = 'entertainment', 'Entertainment'
   SAVINGS = 'savings', 'Savings'
   OTHER = 'other', 'Other'


class Entry(models.Model):
   user = models.ForeignKey(user, on_delete=models.CASCADE, related_name='entries')
   amount = models.DecimalField(max_digits=10, decimal_places=2)
   is_income = models.BooleanField(default=False) # True = income, False = expense
   category = models.CharField(max_length=32, choices=Category.choices, default=Category.OTHER)
   note = models.CharField(max_length=255, blank=True)
   created_at = models.DateTimeField(auto_now_add=True)
   date = models.DateField() # date transaction occurred
   def __str__(self): 
      t = "Income" if self.is_income else "Expense"
      return f"{t} {self.amount} - {self.category}"



class SavingsGoal(models.Model):
   
   user = models.ForeignKey(user, on_delete=models.CASCADE, related_name='goals')
   name = models.CharField(max_length=100)
   target_amount = models.DecimalField(max_digits=12, decimal_places=2)
   saved_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
   deadline = models.DateField(null=True, blank=True)

   def __str__(self):
        return f"{self.name} ({self.saved_amount}/{self.target_amount})"



BASE_DIR = path(__file__).resolve().parent.parent


SECRET_KEY = 'django-insecure-replace-this-with-a-real-secret'


DEBUG = True


ALLOWED_HOSTS = []


INSTALLED_APPS = [
'django.contrib.admin',
'django.contrib.auth',
'djangcontrib.sessions',
'django.contrib.messages',
'django.contrib.staticfiles',
'rest_framework',
'core',
]


MIDDLEWARE = [
'django.middleware.security.SecurityMiddleware',
'django.contrib.sessions.middleware.SessionMiddleware',
'django.middleware.common.CommonMiddleware',
'django.middleware.csrf.CsrfViewMiddleware',
'django.contrib.auth.middleware.AuthenticationMiddleware',
'django.contrib.messages.middleware.MessageMiddleware',
'django.middleware.clickjacking.XFrameOptionsMiddleware',
]


ROOT_URLCONF = 'config.urls'


TEMPLATES = [
{
'BACKEND': 'django.template.backends.django.DjangoTemplates',
'DIRS': [BASE_DIR / 'core' / 'templates'],
'APP_DIRS': True,
'OPTIONS': {
'context_processors': [
'django.template.context_processors.debug',
'django.template.context_processors.request',
'django.contrib.auth.context_processors.auth',
'django.contrib.messages.context_processors.messages',
],
},
},
]


WSGI_APPLICATION = 'config.wsgi.application'


DATABASES = {
'default': {
'ENGINE': 'django.db.backends.sqlite3',
'NAME': BASE_DIR / 'db.sqlite3',
}
}


AUTH_PASSWORD_VALIDATORS = [
{
'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
},
{
'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
},
{
'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
},
{
'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
},
]


LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'Asia/Kolkata'
USE_I18N = True
USE_TZ = True


STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / 'core' / 'static']


DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
from django.contrib import admin
from django.urls import path, include


urlpatterns = [
path('admin/', admin.site.urls),
path('', include('core.urls')),
]

import os
from django.core.wsgi import get_wsgi_application


os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
application = get_wsgi_application()


class CoreConfig(AppConfig):
   
   default_auto_field = 'django.db.models.BigAutoField'
   name = 'core'


class TransactionForm(forms.ModelForm):
   
  date = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}))

  class Meta:
   model = Transaction
   fields = ['category', 'amount', 'note', 'date']


class CategoryForm(forms.ModelForm):
  class Meta: 
    model = Category
fields = ['name', 'is_income']


class SavingsGoalForm(forms.ModelForm):
   
   due_date = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}), required=False)


class Meta:
  
  model = SavingsGoal
fields = ['name', 'target_amount', 'saved_amount', 'due_date']


class RegisterForm(UserCreationForm):
  email = forms.EmailField(required=True)


class Meta:
  model = user
fields = ("username", "email", "password1", "password2")



admin.site.register(Category)
admin.site.register(Transaction)
admin.site.register(SavingsGoal)
admin.site.register(Budget)



app_name = 'core'


urlpatterns = [
path('', views.dashboard, name='dashboard'),
path('transactions/add/', views.add_transaction, name='add_transaction'),
path('reports/', views.reports, name='reports'),
path('login/', views.user_login, name='login'),
path('logout/', views.user_logout, name='logout'),
path('register/', views.register, name='register'),
]

def register(request):
  if request.method == 'POST':
    form = RegisterForm(request.POST)
    if form.is_valid():  
      user = form.save()
      login(request, user)
      return redirect('core:dashboard')
    
  else:
      form = RegisterForm()
  return render(request, 'core/register.html', {'form': form})




def user_login(request):
  if request.method == 'POST':
   username = request.POST.get('username')
   password = request.POST.get('password')
   user = authenticate(request, username=username, password=password)
  if user:

    login(request, user)
    return redirect('core:dashboard')
  else:
   return render(request, 'core/login.html', {'error': 'Invalid credentials'})
   return render(request, 'core/login.html')




def user_logout(request):
  
  logout(request)
  return redirect('core:login')




@login_required
def dashboard(request):
  user = request.user
# quick stats
total_income = Transaction.objects.filter(user=user, category__is_income=True).aggregate(total=Sum('amount'))['total'] or 0
total_expense = Transaction.objects.filter(user=user, category__is_income=False).aggregate(total=Sum('amount'))['total'] or 0
balance = total_income - total_expense


