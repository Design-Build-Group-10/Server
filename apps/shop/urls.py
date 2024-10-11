from django.urls import path

from apps.shop.views import ShopListView, ShopDetailView

urlpatterns = [
    path('', ShopListView.as_view(), name='shop-list'),
    path('<int:shop_id>/', ShopDetailView.as_view(), name='shop-detail'),
]
