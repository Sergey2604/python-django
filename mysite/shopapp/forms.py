# coding=utf-8
from django import forms
from django.contrib.auth.models import Group
from django.forms import ModelForm

from .models import Product, Order


class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = "name", "price", "description", "discount"

    images = forms.ImageField(
        widget = forms.ClearableFileInput(attrs = {'multiple': True})
    )


class OrderForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = 'user', 'products', 'promocode', 'delivery_address'


class GroupForm(ModelForm):
    class Meta:
        model = Group
        fields = 'name',
