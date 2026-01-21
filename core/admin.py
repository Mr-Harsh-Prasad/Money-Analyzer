from django.contrib import admin
from .models import Category, Transaction, SavingsGoal, Budget

# admin.site.register(Category) # Category is an Enum in models.py, cannot register directly unless it's a Model. 
# Wait, in app.py logic line 180 CategoryForm uses model=Category. 
# BUT line 19 Class Category(models.TextChoices).
# This is a CONTRADICTION in the original code. 
# Code at line 207 admin.site.register(Category) implies it is a model.
# Code at line 19 implies it is an Enum.
# Code at line 33 uses it as choices.
# However, to be a Foreign Key or have a Form, it usually needs to be a Model if we want dynamic categories.
# BUT line 33 `category = models.CharField(..., choices=Category.choices)` implies it is indeed just TextChoices.
# If so, `admin.site.register(Category)` will FAIL.
# And `class CategoryForm(forms.ModelForm): class Meta: model = Category` will FAIL.
# I will assume the INTENT was dynamic categories, but the implementation used TextChoices.
# FOR NOW, I will stick to TextChoices as defined in models.py and comment out admin register for it, 
# OR I should convert it to a Model.
# Given "Entry... category = CharField... choices", it strongly suggests hardcoded choices.
# So I will NOT register Category in admin, and I will fix CategoryForm in forms.py later.

admin.site.register(Transaction)
admin.site.register(SavingsGoal)
admin.site.register(Budget)
