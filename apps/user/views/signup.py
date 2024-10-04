# user/views/signup.py
from django.contrib.auth import login
from django.db import transaction
from rest_framework.exceptions import ValidationError
from rest_framework.generics import GenericAPIView
from rest_framework.permissions import AllowAny
from rest_framework_simplejwt.tokens import RefreshToken

from apps.user.models import User
from apps.user.serializers import RegisterSerializer
from common.utils.response import success_response, bad_request_response, internal_error_response


# 用户注册视图
class RegisterView(GenericAPIView):
    authentication_classes = []
    permission_classes = [AllowAny]
    serializer_class = RegisterSerializer
    scene = 'register'

    queryset = User.objects.all()

    @transaction.atomic
    def post(self, request, *args, **kwargs):
        try:
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            user_data = serializer.validated_data
            username = user_data['username']
            password = user_data['password']

            if User.objects.filter(username=username).exists():
                raise ValidationError('UserId already exists.')

            # 创建用户
            user = User.objects.create_user(
                username=username,
                password=password,
                phone=user_data.get('phone', None),
                email=user_data.get('email', None),
            )

            if not request.user.is_authenticated:
                login(request, user)
            refresh = RefreshToken.for_user(user)
            return success_response({
                'refreshToken': str(refresh),
                'accessToken': str(refresh.access_token),
            })
        except ValidationError as e:
            transaction.set_rollback(True)
            return bad_request_response(str(e))
        except Exception as e:
            transaction.set_rollback(True)
            return internal_error_response(f"Unexpected error: {str(e)}")
