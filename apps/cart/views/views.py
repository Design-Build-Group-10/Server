from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework_simplejwt.authentication import JWTAuthentication

from common.utils.response import success_response, bad_request_response
from apps.cart.models import Cart, CartItem
from apps.cart.serializers import CartSerializer, CartItemSerializer
from apps.product.models import Product


class CartView(APIView):
    """
    查看购物车详情
    """
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            cart = Cart.objects.get(user=request.user)
            serializer = CartSerializer(cart)
            return success_response(data={"cart": serializer.data})
        except Cart.DoesNotExist:
            return bad_request_response("Cart not found for the user")
        except Exception as e:
            return bad_request_response(f"Failed to retrieve cart: {str(e)}")


class AddToCartView(APIView):
    """
    添加商品到购物车
    """
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            product_id = request.data.get('product_id')
            quantity = request.data.get('quantity', 1)
            cart = Cart.objects.get_or_create(user=request.user)[0]
            product = Product.objects.get(id=product_id)
            cart_item, created = CartItem.objects.get_or_create(cart=cart, product=product)
            if created:
                cart_item.quantity = quantity
            else:
                cart_item.quantity += quantity
            cart_item.save()
            return success_response(message="Product added to cart")
        except Product.DoesNotExist:
            return bad_request_response(f"Product with id {product_id} not found")
        except Exception as e:
            return bad_request_response(f"Failed to add product to cart: {str(e)}")


class ChangeCartView(APIView):
    """
    修改购物车中商品的数量
    """
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            product_id = request.data.get('product_id')
            quantity = request.data.get('quantity', 1)
            cart = Cart.objects.get_or_create(user=request.user)[0]
            product = Product.objects.get(id=product_id)
            cart_item, created = CartItem.objects.get_or_create(cart=cart, product=product)

            if quantity == 0:
                cart_item.delete()
                return success_response(message="Product removed from cart")
            else:
                cart_item.quantity = quantity
                cart_item.save()
                return success_response(message="Product added to cart")
        except Product.DoesNotExist:
            return bad_request_response(f"Product with id {product_id} not found")
        except Exception as e:
            return bad_request_response(f"Failed to add product to cart: {str(e)}")
