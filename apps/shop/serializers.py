from rest_framework import serializers

from apps.product.serializers import ProductSerializer
from apps.shop.models import Shop


class ShopSerializer(serializers.ModelSerializer):
    startTime = serializers.TimeField(source='start_time', required=False, allow_null=True)
    endTime = serializers.TimeField(source='end_time', required=False, allow_null=True)
    logo = serializers.ImageField(required=False, allow_null=True)

    class Meta:
        model = Shop
        fields = ['id', 'name', 'description', 'promotions', 'featured_products', 'phone', 'email', 'address',
                  'startTime', 'endTime', 'logo']
        extra_kwargs = {
            'promotions': {'required': False},
            'featured_products': {'required': False}
        }


class ShopDetailSerializer(serializers.ModelSerializer):
    featured_products = ProductSerializer(many=True, read_only=True)
    startTime = serializers.TimeField(source='start_time', read_only=True)
    endTime = serializers.TimeField(source='end_time', read_only=True)
    logo = serializers.ImageField(read_only=True)  # Read-only for the detailed view

    class Meta:
        model = Shop
        fields = ['id', 'name', 'description', 'featured_products', 'promotions', 'phone', 'email', 'address',
                  'startTime', 'endTime', 'logo', 'created_at', 'updated_at']
