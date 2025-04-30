from django.forms import ModelForm
# from ecommerce.product.models import Product, ProductImage
from vendor.models import Vendor
from allauth.account.forms import SignupForm
from django import forms
        
        
class VendorApplyForm(forms.ModelForm):
    
    class Meta:
        model = Vendor
        fields = "__all__"  # Will include all fields from Vendor model
        exclude = ["user", "is_approved"]  # 



# class ProductForm(ModelForm):
#     class Meta:
#         model = Product
#         fields = ['category', 'image', 'title', 'description', 'price']

# class ProductImageForm(ModelForm):
#     class Meta:
#         model = ProductImage
#         fields = ['image']
