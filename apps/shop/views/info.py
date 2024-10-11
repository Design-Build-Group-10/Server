from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.views import APIView
from rest_framework_simplejwt.authentication import JWTAuthentication

from apps.shop.models import Shop
from apps.shop.serializers import ShopSerializer
from common.utils.response import success_response, bad_request_response


class ShopListView(APIView):
    """
    获取所有店铺信息
    """
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            shops = Shop.objects.all()
            serializer = ShopSerializer(shops, many=True)
            return success_response(data={"shopList": serializer.data})
        except Exception as e:
            return bad_request_response(f"Failed to retrieve shops: {str(e)}")


class ShopDetailView(APIView):
    """
    获取某个具体店铺的信息
    """
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request, shop_id):
        try:
            shop = Shop.objects.get(id=shop_id)
            serializer = ShopSerializer(shop)
            return success_response(data={"shopInfo": serializer.data})
        except Shop.DoesNotExist:
            return bad_request_response(f"Shop with id {shop_id} not found")
        except Exception as e:
            return bad_request_response(f"Failed to retrieve shop: {str(e)}")


class UserShopListView(APIView):
    """
    获取当前用户所有店铺信息
    """
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAdminUser]

    def get(self, request):
        try:
            # 获取当前用户的店铺
            user = request.user
            shops = Shop.objects.filter(creator=user)
            serializer = ShopSerializer(shops, many=True)
            return success_response(data={"userShops": serializer.data})
        except Exception as e:
            return bad_request_response(f"Failed to retrieve user's shops: {str(e)}")
