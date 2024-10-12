from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.permissions import IsAdminUser
from rest_framework.views import APIView
from rest_framework_simplejwt.authentication import JWTAuthentication

from apps.shop.serializers import ShopSerializer
from common.utils.response import success_response, bad_request_response, internal_error_response


class RegisterShopView(APIView):
    """
    Allows an admin to register a new shop and link it with the current user.
    """
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAdminUser]
    parser_classes = [MultiPartParser, FormParser]

    def post(self, request):
        try:
            serializer = ShopSerializer(data=request.data)
            print(serializer)
            if serializer.is_valid():
                shop = serializer.save(creator=request.user)
                return success_response(data=ShopSerializer(shop).data, message="Shop registered successfully")
            return bad_request_response(message="Invalid data")
        except Exception as e:
            return internal_error_response(message=f"Internal error: {str(e)}")
