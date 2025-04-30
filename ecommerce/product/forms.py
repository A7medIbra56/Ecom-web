from django import forms
from ecommerce.product.models import Product, ProductImage

class AddToCartForm(forms.Form):
    quantity = forms.IntegerField()
    
class ProductForm(forms.ModelForm):
    
    class Meta:
        model = Product
        fields = "__all__"

class ProductImageForm(forms.ModelForm):
    images = forms.FileField(required=False)

    class Meta:
        model = ProductImage
        fields = ["images"]