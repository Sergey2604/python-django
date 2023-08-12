# coding=utf-8
from rest_framework import serializers

from shopapp.models import Product, Order


class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = (
            'pk',
            'name',
            'description',
            'price',
            'discount',
            'created_at',
            'archieved',
            'created_by',
            'preview'
        )


class OrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = (
            'pk',
            'delivery_address',
            'promocode',
            'created_at',
            'user',
            'products',
            'receipt',
        )
