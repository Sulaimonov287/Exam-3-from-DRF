from rest_framework import generics, status, filters
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.contrib.auth.models import User
from .models import Category, Product, CartItem, Order, OrderItem
from .serializers import (
    UserRegisterSerializer, UserProfileSerializer,
    CategorySerializer, ProductSerializer,
    CartItemSerializer, OrderSerializer
)
from .permissions import IsAdminOrReadOnly

class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserRegisterSerializer
    permission_classes = [AllowAny]

class ProfileView(generics.RetrieveAPIView):
    serializer_class = UserProfileSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user

class CategoryListCreateView(generics.ListCreateAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [IsAdminOrReadOnly]

class CategoryDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [IsAdminOrReadOnly]

class ProductListCreateView(generics.ListCreateAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [IsAdminOrReadOnly]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name']
    ordering_fields = ['price']

class ProductDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [IsAdminOrReadOnly]

class CartListCreateView(generics.ListCreateAPIView):
    serializer_class = CartItemSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return CartItem.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        product = serializer.validated_data['product']
        quantity = serializer.validated_data.get('quantity', 1)
        
        item, created = CartItem.objects.get_or_create(
            user=self.request.user,
            product=product,
            defaults={'quantity': quantity}
        )
        if not created:
            item.quantity += quantity
            if item.quantity > product.stock:
                raise serializers.ValidationError(f"Previshen ostatok na sklade ({product.stock} sht.).")
            item.save()

class CartItemDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = CartItemSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return CartItem.objects.filter(user=self.request.user)

class OrderListCreateView(generics.ListCreateAPIView):
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        if self.request.user.is_staff:
            return Order.objects.all()
        return Order.objects.filter(user=self.request.user)

    def create(self, request, *args, **kwargs):
        cart_items = CartItem.objects.filter(user=request.user)
        if not cart_items.exists():
            return Response({"error": "Korzina pustaya!"}, status=status.HTTP_400_BAD_REQUEST)

        for item in cart_items:
            if item.quantity > item.product.stock:
                return Response(
                    {"error": f"Tovara '{item.product.name}' net v nuzhnom kolichestve ({item.product.stock} sht.)."},
                    status=status.HTTP_400_BAD_REQUEST
                )

        total_price = sum(item.product.price * item.quantity for item in cart_items)
        order = Order.objects.create(user=request.user, total_price=total_price)

        for item in cart_items:
            OrderItem.objects.create(
                order=order,
                product=item.product,
                quantity=item.quantity,
                price=item.product.price
            )
            item.product.stock -= item.quantity
            item.product.save()

        cart_items.delete()

        serializer = self.get_serializer(order)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

class OrderDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        if self.request.user.is_staff:
            return Order.objects.all()
        return Order.objects.filter(user=self.request.user)

    def patch(self, request, *args, **kwargs):
        order = self.get_object()

        if not request.user.is_staff:
            if 'status' in request.data and request.data['status'] == 'cancelled':
                if order.status == 'pending':
                    order.status = 'cancelled'
                    order.save()
                    return Response({"message": "Zakaz otmenen."})
                return Response({"error": "Nelzya otmenit obrabotanniy zakaz."}, status=400)
            return Response({"error": "U tebya net prav menjat status."}, status=403)

        return super().patch(request, *args, **kwargs)