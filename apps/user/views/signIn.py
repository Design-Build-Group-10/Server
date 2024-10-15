# user/views/signIn.py
# 用户登录视图
import os
from datetime import timedelta

import cv2
from django.contrib.auth import authenticate, login
from django.core.exceptions import ValidationError
from django.utils import timezone
from rest_framework.generics import GenericAPIView
from rest_framework.parsers import MultiPartParser
from rest_framework.permissions import AllowAny
from rest_framework_simplejwt.tokens import RefreshToken

from apps.user.models import User, Message
from apps.user.serializers import LoginSerializer
from common.utils.chroma_client import face_collection
from common.utils.face_process import process_frame, save_process_record, save_face_image
from common.utils.response import bad_request_response, success_response, internal_error_response


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

            # Check if more than 10 minutes have passed since the last login
            now = timezone.now()
            if user.last_login and (now - user.last_login) > timedelta(minutes=10):
                user.points += 5
                user.save()

                # Create a message notifying the user about their reward points
                Message.objects.create(
                    user=user,
                    title="Reward Points Earned",
                    description="🎉 You have received 5 reward points for logging in.",
                    created_at=now
                )

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
    scene = 'login'  # 登录场景，用于保存到 login 文件夹

    def post(self, request, *args, **kwargs):
        try:
            # 1. 检查是否上传了 face 文件
            face_image = request.FILES.get('face')
            if not face_image:
                return bad_request_response("No face image provided")

            # 2. 保存上传的 face 图像
            face_image_info = save_face_image(self.scene, face_image)
            face_image_path = face_image_info['face_image_path']
            folder = face_image_info['folder']

            # 3. 使用 OpenCV 读取图片文件
            frame = cv2.imread(face_image_path)
            if frame is None:
                return bad_request_response("Invalid image file")

            # 4. 处理图像，检测人脸
            result = process_frame(frame)

            # 5. 检查人脸数量
            num_faces = len(result['processed_faces'])
            if num_faces == 0:
                return bad_request_response("No face detected in the image")
            elif num_faces > 1:
                return bad_request_response("Multiple faces detected. Please upload an image with only one face.")

            # 检查人脸的 identity 是否为 'unknown'
            if result['processed_faces'][0]['identity'] == 'unknown':
                return bad_request_response("Face not recognized in the system")

            # 6. 获取第一个人脸的 embedding
            embedding = result['processed_faces'][0]['embedding']

            # 7. 调用 CHROMA 进行查询，获取 user_id
            query_results = face_collection.query(query_embeddings=[embedding], n_results=1)
            if not query_results['ids'] or not query_results['ids'][0]:
                return bad_request_response("No matching face found in the system")

            user_id = query_results['ids'][0][0]

            # 8. 获取用户信息并生成双 token
            try:
                user = User.objects.get(username=user_id)
            except User.DoesNotExist:
                return bad_request_response(f"User with username '{user_id}' not found")

            # Check if more than 10 minutes have passed since the last login
            now = timezone.now()
            if user.last_login and (now - user.last_login) > timedelta(minutes=10):
                # Increase user's points by 5
                user.points += 5
                user.save()

                # Create a message notifying the user about their reward points
                Message.objects.create(
                    user=user,
                    title="Reward Points Earned",
                    description="🎉 You have received 5 reward points for logging in.",
                    created_at=now
                )

            # 生成 JWT token
            refresh = RefreshToken.for_user(user)

            # 9. 保存处理记录到数据库
            frame_path = os.path.join(folder, 'processed_frame.jpg')
            key_points_image_path = os.path.join(folder, 'key_points_image.jpg')
            cv2.imwrite(frame_path, result['frame'])
            cv2.imwrite(key_points_image_path, result['key_points_image'])

            save_process_record(
                folder=folder,
                face_image_path=face_image_path,
                frame_path=frame_path,
                key_points_image_path=key_points_image_path,
                result=result
            )

            # 10. 返回 token
            return success_response({
                'refreshToken': str(refresh),
                'accessToken': str(refresh.access_token)
            })

        except Exception as e:
            # 捕获所有其他异常并返回内部错误响应
            return internal_error_response(f"Failed to process face login: {str(e)}")
