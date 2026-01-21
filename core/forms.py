from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import Transaction, SavingsGoal, Category

class TransactionForm(forms.ModelForm):
   date = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}))

   class Meta:
    model = Transaction
    fields = ['category', 'amount', 'note', 'date']

class CategoryForm(forms.Form):
  # Since Category is TextChoices, we can't use ModelForm for it efficiently unless we wrap it.
  # But the original code was confused. I will make a simple form that mimics what might be needed,
  # or better yet, since it's hardcoded choices, we don't really 'create' categories in the DB.
  # I'll comment this out or make it a ChoiceField form if needed.
  # For now, I'll just leave it as valid python but unrelated to a model save.
  name = forms.ChoiceField(choices=Category.choices)
  is_income = forms.BooleanField(required=False)

class SavingsGoalForm(forms.ModelForm):
   due_date = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}), required=False)

   class Meta:
     model = SavingsGoal
     fields = ['name', 'target_amount', 'saved_amount', 'due_date']
     # Note: 'deadline' is in model, 'due_date' is in form. I need to alias them or fix model.
     # Model has 'deadline'. Form has 'due_date'.
     # I will map due_date to deadline in views or rename in form.
     # Let's rename in Meta to match Model.
     # But wait, logic might rely on 'due_date'.
     # I'll keep 'due_date' in form field definition but Map it to 'deadline' in Meta if possible, 
     # OR just rename field in form to 'deadline'.
     
   def __init__(self, *args, **kwargs):
      super().__init__(*args, **kwargs)
      self.fields['deadline'] = self.fields.pop('due_date')

   class Meta:
      model = SavingsGoal
      fields = ['name', 'target_amount', 'saved_amount', 'deadline']


class RegisterForm(UserCreationForm):
  email = forms.EmailField(required=True)

  class Meta:
    model = User
    fields = ("username", "email")
