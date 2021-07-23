from django.contrib.auth import get_user_model
from django import forms
from .models import (
    OrderItem, Product, Payment, Customer
)

User = get_user_model()


class AddToCartForm(forms.ModelForm):

    class Meta:
        model = OrderItem
        fields = ['price', 'discount']

    def __init__(self, *args, **kwargs):
        self.product_id = kwargs.pop('product_id')
        product = Product.objects.get(id=self.product_id)
        super().__init__(*args, **kwargs)

class PaymentForm(forms.ModelForm):
    price = forms.FloatField()

    class Meta:
        model = Payment
        fields = ['method', 'price']

class CustomerForm(forms.ModelForm):

    class Meta:
        model = Customer
        fields = ['name','lastname','phone','email']
