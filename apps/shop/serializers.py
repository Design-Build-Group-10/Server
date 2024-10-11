from rest_framework import serializers

from apps.product.serializers import ProductSerializer
from apps.shop.models import Shop


class ShopSerializer(serializers.ModelSerializer):
    featured_products = ProductSerializer(many=True, read_only=True)

    class Meta:
        model = Shop
        fields = ['id', 'name', 'description', 'featured_products', 'promotions']
