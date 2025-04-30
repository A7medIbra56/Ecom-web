from django import forms

##############################################
# Vendor Forms
##############################################
from vendor.models import Vendor
from ecommerce.product.models import Product

class VendorUpdateForm(forms.ModelForm):
    class Meta:
        model = Vendor
        exclude = ["is_approved", "created_at"]  # Fields you want to exclude

class ProductUpdateForm(forms.ModelForm):
    class Meta:
        model = Product
        exclude = ["is_approved", "created_at"]  # Fields you want to exclude

##############################################
# Category Forms
##############################################     
from ecommerce.product.models import Category, SubCategory

class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['title', 'slug', 'commission_rate']

class SubCategoryForm(forms.ModelForm):
    class Meta:
        model = SubCategory
        fields = ['title', 'commission_rate']