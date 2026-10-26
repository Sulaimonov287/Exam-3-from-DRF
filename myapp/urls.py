from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from .views import (
    RegisterView, ProfileView,
    CategoryListCreateView, CategoryDetailView,
    ProductListCreateView, ProductDetailView,
    CartListCreateView, CartItemDetailView,
    OrderListCreateView, OrderDetailView
)

urlpatterns = [
    # Авторизация и JWT
    path('auth/register/', RegisterView.as_view(), name='auth_register'),
    path('auth/login/', TokenObtainPairView.as_view(), name='auth_login'),
    path('auth/refresh/', TokenRefreshView.as_view(), name='auth_refresh'),
    path('auth/profile/', ProfileView.as_view(), name='auth_profile'),

    # Категории
    path('categories/', CategoryListCreateView.as_view(), name='categories_list'),
    path('categories/<int:pk>/', CategoryDetailView.as_view(), name='categories_detail'),

    # Товары
    path('products/', ProductListCreateView.as_view(), name='products_list'),
    path('products/<int:pk>/', ProductDetailView.as_view(), name='products_detail'),

    # Корзина
    path('cart/', CartListCreateView.as_view(), name='cart_list'),
    path('cart/<int:pk>/', CartItemDetailView.as_view(), name='cart_detail'),

    # Заказы
    path('orders/', OrderListCreateView.as_view(), name='orders_list'),
    path('orders/<int:pk>/', OrderDetailView.as_view(), name='orders_detail'),
]