from rest_framework import serializers

from apps.cart.models import CartItem, Cart


class CartItemSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(source='product.id', read_only=True)
    name = serializers.CharField(source='product.name', read_only=True)
    description = serializers.CharField(source='product.description', read_only=True)
    price = serializers.DecimalField(source='product.price', max_digits=10, decimal_places=2, read_only=True)
    image = serializers.ImageField(source='product.image', read_only=True)
    created_at = serializers.DateTimeField(source='product.created_at', read_only=True)
    updated_at = serializers.DateTimeField(source='product.updated_at', read_only=True)
    quantity = serializers.IntegerField(read_only=True)
    total_price = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)

    class Meta:
        model = CartItem
        fields = ['id', 'name', 'description', 'price', 'image', 'created_at', 'updated_at', 'quantity', 'total_price']


class CartSerializer(serializers.ModelSerializer):
    products = CartItemSerializer(source='cartitem_set', many=True, read_only=True)
    total_quantity = serializers.SerializerMethodField()
    total_price = serializers.SerializerMethodField()

    class Meta:
        model = Cart
        fields = ['products', 'total_quantity', 'total_price']

    def get_total_quantity(self, obj):
        return sum(item.quantity for item in obj.cartitem_set.all())

    def get_total_price(self, obj):
        return sum(item.quantity * item.product.price for item in obj.cartitem_set.all())
