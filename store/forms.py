# forms.py
from django import forms
from .models import Product

class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['name', 'slug', 'category', 'price', 'description', 'available', 'image']
        
class ProductStockForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['available','price','description']  # O cualquier campo relacionado con bodega, por ejemplo stock si lo tienes