from django.urls import path

from apps.cart.views.views import CartView, AddToCartView, ChangeCartView

urlpatterns = [
    path('', CartView.as_view(), name='cart-detail'),
    path('add/', AddToCartView.as_view(), name='add-to-cart'),
    path('change/', ChangeCartView.as_view(), name='change-cart'),
]
