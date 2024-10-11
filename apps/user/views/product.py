from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework_simplejwt.authentication import JWTAuthentication

from apps.user.serializers import AddressSerializer, FavoriteProductSerializer, FollowedShopsSerializer, \
    BrowseHistorySerializer
from common.utils.response import success_response, internal_error_response


class UserAddressView(APIView):
    """
    获取用户的收货地址
    """
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            serializer = AddressSerializer(request.user)
            return success_response(data=serializer.data)
        except Exception as e:
            return internal_error_response(message=f"Failed to retrieve shipping address: {str(e)}")


class UserFavoriteProductsView(APIView):
    """
    获取用户收藏的商品
    """
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            serializer = FavoriteProductSerializer(request.user)
            return success_response(data=serializer.data)
        except Exception as e:
            return internal_error_response(message=f"Failed to retrieve favorite products: {str(e)}")


class UserFollowedShopsView(APIView):
    """
    获取用户关注的店铺
    """
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            serializer = FollowedShopsSerializer(request.user)
            return success_response(data=serializer.data)
        except Exception as e:
            return internal_error_response(message=f"Failed to retrieve followed shops: {str(e)}")


class UserBrowseHistoryView(APIView):
    """
    获取用户的浏览历史
    """
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            serializer = BrowseHistorySerializer(request.user)
            return success_response(data=serializer.data)
        except Exception as e:
            return internal_error_response(message=f"Failed to retrieve browse history: {str(e)}")
