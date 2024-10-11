from django.contrib.auth import get_user_model
from django.db import models

from apps.product.models import Product

User = get_user_model()


class Shop(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField()
    featured_products = models.ManyToManyField(Product, related_name='featured_in_shops')
    promotions = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    creator = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_shops')

    def __str__(self):
        return self.name
