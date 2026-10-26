from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Category, Product, CartItem, Order, OrderItem

class UserRegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'password']

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data.get('email', ''),
            password=validated_data['password']
        )
        return user

class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'is_staff')

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'

class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = '__all__'

class CartItemSerializer(serializers.ModelSerializer):
    product_detail = ProductSerializer(source='product', read_only=True)

    class Meta:
        model = CartItem
        fields = ('id', 'product', 'product_detail', 'quantity')

    def validate(self, attrs):
        product = attrs.get('product')
        quantity = attrs.get('quantity', 1)

        if product and quantity > product.stock:
            raise serializers.ValidationError(f'Na sklade dostupno tolko {product.stock} shtuk tovara!')
        return attrs

class OrderItemSerializer(serializers.ModelSerializer):
    product_name = serializers.ReadOnlyField(source='product.name')

    class Meta:
        model = OrderItem
        fields = ('id', 'product', 'product_name', 'quantity', 'price')

class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)

    class Meta:
        model = Order
        fields = ('id', 'user', 'created_at', 'total_price', 'status', 'items')
        read_only_fields = ('user', 'total_price', 'created_at')