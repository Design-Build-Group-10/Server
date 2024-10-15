# user/serializers.py

from django.contrib.auth.hashers import make_password
from rest_framework import serializers

from apps.user.models import User


class UserSerializer(serializers.ModelSerializer):
    role = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'phone', 'avatar', 'face', 'shipping_address',
                  'payment_method', 'role', 'points')
        read_only_fields = ['id', 'username', 'face', 'created_at', 'updated_at', 'points']

    def get_role(self, obj):
        return 'admin' if obj.is_staff else 'user'


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


class AddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['shipping_address']


class FavoriteProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['favorite_products']


class FollowedShopsSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['followed_shops']


class BrowseHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['browse_history']
