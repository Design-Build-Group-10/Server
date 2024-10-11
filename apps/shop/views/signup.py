from rest_framework.views import APIView
from rest_framework.permissions import IsAdminUser
from rest_framework_simplejwt.authentication import JWTAuthentication

from apps.shop.serializers import ShopSerializer
from common.utils.response import success_response, bad_request_response, internal_error_response


class RegisterShopView(APIView):
    """
    允许管理员注册新店铺，并与当前用户绑定
    """
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAdminUser]

    def post(self, request):
        try:
            serializer = ShopSerializer(data=request.data)
            if serializer.is_valid():
                shop = serializer.save(creator=request.user)  # 将当前登录用户设为店铺创建者
                return success_response(data=ShopSerializer(shop).data, message="Shop registered successfully")
            return bad_request_response(message="Invalid data")
        except Exception as e:
            return internal_error_response(message=f"Internal error: {str(e)}")
