# user/views/signIn.py
# 用户登录视图
import os
import uuid

import cv2
from django.contrib.auth import authenticate, login
from django.core.exceptions import ValidationError
from rest_framework.generics import GenericAPIView
from rest_framework.parsers import MultiPartParser
from rest_framework.permissions import AllowAny
from rest_framework_simplejwt.tokens import RefreshToken

from apps.user.models import User
from apps.user.serializers import LoginSerializer
from common.utils.chroma_client import face_collection
from common.utils.face_process import process_frame
from common.utils.response import bad_request_response, success_response, internal_error_response
from config import settings


class LoginView(GenericAPIView):
    authentication_classes = []
    permission_classes = [AllowAny]
    serializer_class = LoginSerializer
    scene = 'login'

    def post(self, request, *args, **kwargs):
        try:
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            username = serializer.validated_data.get('username')
            password = serializer.validated_data.get('password')

            if not username or not password:
                return bad_request_response("Username and password are required")

            user = authenticate(username=username, password=password)

            if not user:
                return bad_request_response('用户名或密码错误')

            login(request, user)
            refresh = RefreshToken.for_user(user)

            return success_response({
                'refreshToken': str(refresh),
                'accessToken': str(refresh.access_token)
            })

        except ValidationError as e:
            return bad_request_response(str(e))
        except Exception as e:
            return internal_error_response(f"Unexpected error: {str(e)}")


class FaceLoginView(GenericAPIView):
    authentication_classes = []
    permission_classes = [AllowAny]
    parser_classes = [MultiPartParser]

    def post(self, request, *args, **kwargs):
        try:
            # 1. 检查是否上传了face文件
            face_image = request.FILES.get('face')
            if not face_image:
                return bad_request_response("No face image provided")

            # 2. 创建一个唯一的文件夹来保存上传的face图像
            unique_folder = os.path.join(str(settings.MEDIA_ROOT), 'temp_face_images', str(uuid.uuid4()))
            os.makedirs(unique_folder, exist_ok=True)

            # 3. 保存上传的face图像到该文件夹中
            face_image_path = os.path.join(unique_folder, str(uuid.uuid4()) + ".jpg")
            with open(face_image_path, 'wb+') as destination:
                for chunk in face_image.chunks():
                    destination.write(chunk)

            # 4. 使用 OpenCV 读取图片文件
            frame = cv2.imread(face_image_path)
            if frame is None:
                return bad_request_response("Invalid image file")

            # 5. 处理图像，检测人脸
            result = process_frame(frame)

            # 6. 检查人脸数量
            num_faces = len(result['processed_faces'])
            if num_faces == 0:
                return bad_request_response("No face detected in the image")
            elif num_faces > 1:
                return bad_request_response("Multiple faces detected. Please upload an image with only one face.")

            if result['processed_faces'][0]['identity'] == 'unknown':
                return bad_request_response("Face not recognized in the system")

            # 7. 获取第一个人脸的embedding
            embedding = result['processed_faces'][0]['embedding']

            # 8. 调用CHROMA进行查询，获取user_id
            query_results = face_collection.query(query_embeddings=[embedding], n_results=1)

            if not query_results['ids'] or not query_results['ids'][0]:
                return bad_request_response("No matching face found in the system")

            user_id = query_results['ids'][0][0]

            # 9. 获取用户信息并生成双token
            try:
                user = User.objects.get(username=user_id)
            except User.DoesNotExist:
                return bad_request_response(f"User with username '{user_id}' not found")

            # 生成 JWT token
            refresh = RefreshToken.for_user(user)

            # 返回 token
            return success_response({
                'refreshToken': str(refresh),
                'accessToken': str(refresh.access_token)
            })

        except Exception as e:
            # 捕获所有其他异常并返回内部错误响应
            return internal_error_response(f"Failed to process face login: {str(e)}")
