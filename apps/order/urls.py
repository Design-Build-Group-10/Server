from django.urls import path

from apps.order.views.views import OrderListView, OrderDetailView

urlpatterns = [
    path('', OrderListView.as_view(), name='order-list'),
    path('<int:order_id>/', OrderDetailView.as_view(), name='order-detail'),
]
