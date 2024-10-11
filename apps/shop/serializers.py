from rest_framework import serializers
from apps.shop.models import Shop
from apps.product.serializers import ProductSerializer


class ShopSerializer(serializers.ModelSerializer):
    class Meta:
        model = Shop
        fields = ['id', 'name', 'description', 'promotions', 'featured_products']
        extra_kwargs = {
            'featured_products': {'required': False}  # featured_products 字段不是必须的
        }


class ShopDetailSerializer(serializers.ModelSerializer):
    featured_products = ProductSerializer(many=True, read_only=True)

    class Meta:
        model = Shop
        fields = ['id', 'name', 'description', 'featured_products', 'promotions', 'created_at', 'updated_at']
