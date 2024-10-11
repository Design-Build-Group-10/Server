from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework_simplejwt.authentication import JWTAuthentication

from apps.product.models import Product
from apps.product.serializers import ProductSerializer
from common.utils.response import success_response, bad_request_response


class ProductListView(APIView):
    """
    获取所有商品
    """
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            products = Product.objects.all()
            serializer = ProductSerializer(products, many=True)
            return success_response(data={"productList": serializer.data})
        except Exception as e:
            return bad_request_response(f"Failed to retrieve products: {str(e)}")


class ProductDetailView(APIView):
    """
    获取某个具体商品的信息
    """
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request, product_id):
        try:
            product = Product.objects.get(id=product_id)
            serializer = ProductSerializer(product)
            return success_response(data={"productInfo": serializer.data})
        except Product.DoesNotExist:
            return bad_request_response(f"Product with id {product_id} not found")
        except Exception as e:
            return bad_request_response(f"Failed to retrieve product: {str(e)}")