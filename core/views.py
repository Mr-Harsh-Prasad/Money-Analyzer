from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.db.models import Sum
from .models import Transaction, SavingsGoal, Category
from .forms import RegisterForm, TransactionForm

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

import json
from django.utils import timezone
from datetime import datetime
from django.db.models import Sum
from django.core.serializers.json import DjangoJSONEncoder

@login_required
def dashboard(request):
  user = request.user
  now = timezone.now()
  current_month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
  
  # --- Budget Logic ---
  # Simple budget implementation: One budget object per user (or per month).
  # For simplicity, we'll try to get a 'current month' budget or a general one.
  # Let's check models.py: Budget has 'month'.
  # We will try to get the budget for this month.
  from .models import Budget
  try:
      budget_obj = Budget.objects.get(user=user, month__year=now.year, month__month=now.month)
      current_budget = budget_obj.limit
  except Budget.DoesNotExist:
      current_budget = 0

  # --- Quick Stats ---
  total_income = Transaction.objects.filter(user=user, is_income=True).aggregate(total=Sum('amount'))['total'] or 0
  total_expense = Transaction.objects.filter(user=user, is_income=False).aggregate(total=Sum('amount'))['total'] or 0
  balance = total_income - total_expense
  
  # Expense this month
  this_month_expense = Transaction.objects.filter(
      user=user, is_income=False, date__gte=current_month_start
  ).aggregate(total=Sum('amount'))['total'] or 0

  transactions = Transaction.objects.filter(user=user).order_by('-date', '-created_at')[:5]

  context = {
      'total_income': total_income,
      'total_expense': total_expense,
      'balance': balance,
      'transactions': transactions,
      'current_budget': current_budget,
      'this_month_expense': this_month_expense,
  }

  return render(request, 'core/dashboard.html', context)

@login_required
def add_transaction(request):
    if request.method == 'POST':
        form = TransactionForm(request.POST)
        if form.is_valid():
            transaction = form.save(commit=False)
            transaction.user = request.user
            
            # Handle Transaction Type (Income/Expense)
            txn_type = request.POST.get('type')
            if txn_type == 'income':
                transaction.is_income = True
            else:
                transaction.is_income = False
                
            transaction.save()
            return redirect('core:dashboard')
    else:
        form = TransactionForm()
    return render(request, 'core/add_transaction.html', {'form': form})

@login_required
def clear_data(request):
    if request.method == 'POST':
        from .models import Transaction
        Transaction.objects.filter(user=request.user).delete()
    return redirect('core:dashboard')

@login_required
def reports(request):
    return render(request, 'core/reports.html')

@login_required
def profile(request):
    return render(request, 'core/profile.html')

@login_required
def save_budget(request):
    if request.method == 'POST':
        amount = request.POST.get('budget_amount')
        from .models import Budget
        from django.utils import timezone
        now = timezone.now()
        # Update or Create budget for this month
        budget, created = Budget.objects.get_or_create(
            user=request.user, 
            month__year=now.year, 
            month__month=now.month,
            defaults={'limit': amount, 'month': now.date()}
        )
        if not created:
            budget.limit = amount
            budget.save()
            
        return redirect('core:dashboard')
    return redirect('core:dashboard')
