from django.db import models

from apps.product.models import Product


class Shop(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField()
    featured_products = models.ManyToManyField(Product, related_name='featured_in_shops')
    promotions = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name
