from rest_framework import serializers
from .models import *

class ProductSerializer(serializers.ModelSerializer): #Serializers for product to make data in json
    stock = serializers.IntegerField(source='inventory.quantity', read_only=True)

    class Meta:
        model = Product 
        fields = '__all__'


class DealerSerializer(serializers.ModelSerializer): #Serializers for Dealer to make data in json
    class Meta:
        model = Dealer
        fields = '__all__'


class OrderItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderItem
        fields = '__all__'


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)

    class Meta:
        model = Order
        fields = '__all__'


class InventorySerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source='product.name', read_only=True)
    sku = serializers.CharField(source='product.sku', read_only=True)
    price = serializers.DecimalField(source='product.price', max_digits=10, decimal_places=2, read_only=True)

    class Meta:
        model = Inventory
        fields = ['id', 'product', 'product_name', 'sku', 'price', 'quantity', 'updated_at']
