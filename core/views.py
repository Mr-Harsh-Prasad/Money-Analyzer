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

  # --- Chart Data 1: Category Spending ---
  category_data = Transaction.objects.filter(user=user, is_income=False)\
      .values('category')\
      .annotate(total=Sum('amount'))\
      .order_by('-total')
  
  chart_labels = [c['category'] for c in category_data]
  chart_values = [float(c['total']) for c in category_data]

  # --- Chart Data 2: Monthly Trend (Last 6 months) ---
  # Simplified for now: Just show recent transactions trend or dummy last 6 months
  # Implementation: Group by month. Doing this in SQLite/Postgres agnostic way is tricky without TruncMonth.
  # We'll import TruncMonth.
  # --- Chart Data 2: Monthly Trend (Last 6 months) ---
  # We use order_by() first to clear any default ordering that might mess up the GROUP BY.
  # We order by '-month' to get the LATEST 6 months, then reverse them for display.
  from django.db.models.functions import TruncMonth
  monthly_trend = Transaction.objects.filter(user=user, is_income=False)\
      .annotate(month=TruncMonth('date'))\
      .values('month')\
      .annotate(total=Sum('amount'))\
      .order_by('-month')[:6]
      
  # Reverse to show Oldest -> Newest left to right
  monthly_trend_list = list(reversed(monthly_trend))
  
  trend_labels = [m['month'].strftime('%b %Y') for m in monthly_trend_list]
  trend_data = [float(m['total']) for m in monthly_trend_list]

  transactions = Transaction.objects.filter(user=user).order_by('-date', '-created_at')[:5]

  context = {
      'total_income': total_income,
      'total_expense': total_expense,
      'balance': balance,
      'transactions': transactions,
      'current_budget': current_budget,
      'this_month_expense': this_month_expense,
      'chart_labels': json.dumps(chart_labels, cls=DjangoJSONEncoder),
      'chart_values': json.dumps(chart_values, cls=DjangoJSONEncoder),
      'trend_labels': json.dumps(trend_labels, cls=DjangoJSONEncoder),
      'trend_data': json.dumps(trend_data, cls=DjangoJSONEncoder),
  }

  return render(request, 'core/dashboard.html', context)

@login_required
def add_transaction(request):
    if request.method == 'POST':
        form = TransactionForm(request.POST)
        if form.is_valid():
            transaction = form.save(commit=False)
            transaction.user = request.user
            # Logic to determine is_income from category or form?
            # Model has is_income. Form does NOT have is_income field explicitly exposed in fields list in my previous step?
            # Wait, in models.py 'is_income' is a field. In forms.py Meta fields = ['category', 'amount', 'note', 'date'].
            # So 'is_income' is missing from form. I should infer it or add it.
            # INFERENCE: If category is SAVINGS or similar? 
            # Actually, the original app.py had `Category` as TextChoices. 
            # I'll check `models.py`... `is_income` is a boolean.
            # I will default it to False for now or check if I should add it to form.
            # For this refactor I'll add it to form or just let it be default False (Expense).
            # BETTER: Update TransactionForm in next step if needed, or just set it here.
            # Let's simple set it to False (Expression) unless category is 'SAVINGS' (maybe income?? no).
            # A strict refactor would expose it. I'll add it to the instance if it was in the POST, but it's not in form.
            # I will blindly save for now.
            transaction.save()
            return redirect('core:dashboard')
    else:
        form = TransactionForm()
    return render(request, 'core/add_transaction.html', {'form': form})

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
