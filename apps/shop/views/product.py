from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.permissions import IsAdminUser
from rest_framework.views import APIView
from rest_framework_simplejwt.authentication import JWTAuthentication

from apps.product.models import Product
from apps.product.serializers import ProductSerializer
from apps.shop.models import Shop
from common.utils.response import success_response, not_found_response, internal_error_response, bad_request_response, \
    unauthorized_response


class AddProductToShopView(APIView):
    """
    允许管理员向店铺中添加新创建的商品
    """
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAdminUser]
    parser_classes = [MultiPartParser, FormParser]  # 支持 multipart/form-data

    def post(self, request, shop_id):
        try:
            shop = Shop.objects.get(id=shop_id)  # 获取 shop 对象

            # 检查当前用户是否为店铺的创建者
            if shop.creator != request.user:
                return unauthorized_response(message="You are not authorized to manage this shop")

            # 使用 ProductSerializer 来验证并创建新商品
            serializer = ProductSerializer(data=request.data)
            if serializer.is_valid():
                product = serializer.save()  # 保存新商品
                shop.featured_products.add(product)  # 将新商品添加到 shop 的 featured_products 中
                return success_response(data=ProductSerializer(product).data,
                                        message="Product created and added to shop successfully")
            return bad_request_response(message="Invalid product data")

        except Shop.DoesNotExist:
            return not_found_response(message="Shop not found")
        except Exception as e:
            return internal_error_response(message=f"Internal error: {str(e)}")


class RemoveProductFromShopView(APIView):
    """
    允许管理员从店铺中删除商品
    """
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAdminUser]

    def delete(self, request, shop_id, product_id):
        try:
            shop = Shop.objects.get(id=shop_id)

            # 检查当前用户是否为店铺的创建者
            if shop.creator != request.user:
                return unauthorized_response(message="You are not authorized to manage this shop")

            product = Product.objects.get(id=product_id)
            shop.featured_products.remove(product)  # 从店铺中移除商品
            product.delete()
            return success_response(message="Product removed from shop successfully")
        except Shop.DoesNotExist:
            return not_found_response(message="Shop not found")
        except Product.DoesNotExist:
            return not_found_response(message="Product not found")
        except Exception as e:
            return internal_error_response(message=f"Internal error: {str(e)}")


class UpdateProductView(APIView):
    """
    允许管理员修改商品信息
    支持 multipart/form-data 格式，接收图片等文件
    """
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAdminUser]
    parser_classes = [MultiPartParser, FormParser]

    def post(self, request, product_id):
        try:
            product = Product.objects.get(id=product_id)

            # 找到关联的店铺，并检查用户权限
            shop = Shop.objects.filter(featured_products=product).first()
            if not shop or shop.creator != request.user:
                return unauthorized_response(message="You are not authorized to manage this shop")

            # 如果 image 字段不在 request.data 中，则清空数据库中的 image 字段
            if 'image' not in request.data:
                product.image = None  # 清空 image 字段
                product.save(update_fields=['image'])  # 保存更新

            # 处理全量更新，覆盖其他字段
            serializer = ProductSerializer(product, data=request.data)
            if serializer.is_valid():
                serializer.save()
                return success_response(data=serializer.data, message="Product updated successfully")
            return bad_request_response(message="Invalid data")
        except Product.DoesNotExist:
            return not_found_response(message="Product not found")
        except Exception as e:
            return internal_error_response(message=f"Internal error: {str(e)}")
