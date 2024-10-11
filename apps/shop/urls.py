from django.urls import path

from apps.shop.views.info import ShopListView, ShopDetailView
from apps.shop.views.product import AddProductToShopView, UpdateProductView, RemoveProductFromShopView
from apps.shop.views.signup import RegisterShopView

urlpatterns = [
    path('', ShopListView.as_view(), name='shop-list'),
    path('<int:shop_id>/', ShopDetailView.as_view(), name='shop-detail'),
    path('register/', RegisterShopView.as_view(), name='register-shop'),
    path('<int:shop_id>/add-product/', AddProductToShopView.as_view(), name='add-product-to-shop'),
    path('<int:shop_id>/remove-product/<int:product_id>/', RemoveProductFromShopView.as_view(),
         name='remove-product-from-shop'),
    path('update-product/<int:product_id>/', UpdateProductView.as_view(), name='update-product'),
]
