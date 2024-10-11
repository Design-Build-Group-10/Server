from django.db import models

from apps.product.models import Product
from apps.user.models import User

ORDER_STATUS_CHOICES = [
    ('pending', '待付款'),
    ('shipped', '待收货'),
    ('received', '已收货'),
    ('reviewed', '已评价'),
    ('returned', '退换货'),
]


class Order(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    products = models.ManyToManyField(Product, through='OrderItem')
    status = models.CharField(max_length=10, choices=ORDER_STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
