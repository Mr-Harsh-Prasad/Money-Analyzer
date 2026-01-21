from django.db import models
from django.contrib.auth.models import User

class Category(models.TextChoices):
   FOOD = 'food', 'Food'
   TRANSPORT = 'transport', 'Transport'
   BILLS = 'bills', 'Bills' 
   ENTERTAINMENT = 'entertainment', 'Entertainment'
   SAVINGS = 'savings', 'Savings'
   OTHER = 'other', 'Other'

# Renamed Entry to Transaction as per usage elsewhere
class Transaction(models.Model):
   user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='entries')
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
   user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='goals')
   name = models.CharField(max_length=100)
   target_amount = models.DecimalField(max_digits=12, decimal_places=2)
   saved_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
   deadline = models.DateField(null=True, blank=True)

   def __str__(self):
        return f"{self.name} ({self.saved_amount}/{self.target_amount})"

class Budget(models.Model):
    # Budget was registered in admin but not defined in models. Creating a placeholder.
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='budgets')
    limit = models.DecimalField(max_digits=10, decimal_places=2)
    month = models.DateField() 
    
    def __str__(self):
        return f"Budget for {self.month}"
