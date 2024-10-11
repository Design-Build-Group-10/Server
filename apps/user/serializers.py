# user/serializers.py

from django.contrib.auth.hashers import make_password
from rest_framework import serializers

from apps.product.serializers import ProductSerializer
from apps.shop.serializers import ShopSerializer
from apps.user.models import User


class UserSerializer(serializers.ModelSerializer):
    favorite_products = ProductSerializer(many=True, read_only=True)
    followed_shops = ShopSerializer(many=True, read_only=True)
    browse_history = ProductSerializer(many=True, read_only=True)

    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'phone', 'avatar', 'face', 'shipping_address',
                  'payment_method', 'favorite_products', 'followed_shops', 'browse_history')
        read_only_fields = ['id', 'username', 'face', 'created_at', 'updated_at']


class LoginSerializer(serializers.ModelSerializer):
    username = serializers.CharField(label='用户名', max_length=128)
    password = serializers.CharField(label='密码', write_only=True)

    class Meta:
        model = User
        fields = ['username', 'password']


class RegisterSerializer(serializers.ModelSerializer):
    # 将 email, phone, avatar 设置为可选
    email = serializers.EmailField(required=False, allow_blank=True)
    phone = serializers.CharField(required=False, allow_blank=True)
    avatar = serializers.ImageField(required=False, allow_null=True)

    class Meta:
        model = User
        fields = ('username', 'password', 'email', 'phone', 'avatar')

    def create(self, validated_data):
        # 确保密码以加密形式存储
        validated_data['password'] = make_password(validated_data['password'])
        return super(RegisterSerializer, self).create(validated_data)
