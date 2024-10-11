# user/views/signup.py
import os
import re

import cv2
from django.contrib.auth import login
from django.db import transaction
from rest_framework.exceptions import ValidationError
from rest_framework.generics import GenericAPIView
from rest_framework.permissions import AllowAny
from rest_framework_simplejwt.tokens import RefreshToken

from apps.cart.models import Cart
from apps.user.models import User
from apps.user.serializers import RegisterSerializer, UserSerializer
from common.utils.chroma_client import save_to_chroma
from common.utils.face_process import process_frame, save_face_image, save_process_record
from common.utils.response import success_response, bad_request_response, internal_error_response


# 用户注册视图
class RegisterView(GenericAPIView):
    authentication_classes = []
    permission_classes = [AllowAny]
    serializer_class = RegisterSerializer
    scene = 'register'  # 注册场景，保存到 'register' 文件夹

    queryset = User.objects.all()

    @transaction.atomic
    def post(self, request, *args, **kwargs):
        try:
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            user_data = serializer.validated_data
            username = user_data['username']
            password = user_data['password']
            email = user_data.get('email', None)
            phone = user_data.get('phone', None)

            # 检测 email 和 phone 的格式
            if email and not self.is_valid_email(email):
                return bad_request_response("Invalid email format")
            if phone and not self.is_valid_phone(phone):
                return bad_request_response("Invalid phone format")

            # 检查用户名是否已存在
            if User.objects.filter(username=username).exists():
                raise ValidationError('UserId already exists.')

            # 检查是否上传了face文件（必填）
            if 'face' not in request.FILES:
                return bad_request_response("face is required")

            face_image = request.FILES.get('face')

            # 通过 save_face_image 保存上传的 face 图像
            res = save_face_image(self.scene, face_image)
            face_image_path = res['face_image_path']
            folder = res['folder']

            # 使用 OpenCV 读取图片文件
            frame = cv2.imread(face_image_path)
            if frame is None:
                raise ValidationError("Invalid image file")

            # 处理图像，检测人脸
            result = process_frame(frame)

            # 检查人脸数量
            num_faces = len(result['processed_faces'])
            if num_faces == 0:
                raise ValidationError("No face detected in the image")
            elif num_faces > 1:
                raise ValidationError("Multiple faces detected. Please upload an image with only one face.")

            # 检查人脸的 identity 是否为 'unknown'
            if result['processed_faces'][0]['identity'] != 'unknown':
                # 如果 identity 不是 'unknown'，从数据库中查找这个用户并返回其信息
                user_id = result['processed_faces'][0]['identity']
                try:
                    existing_user = User.objects.get(username=user_id)
                except User.DoesNotExist:
                    return bad_request_response(f"User with username '{user_id}' not found")

                return success_response(data={"user": UserSerializer(existing_user).data},
                                        message='Face already exists in the system. Registration not allowed.')

            # 获取第一个人脸的 embedding
            embedding = result['processed_faces'][0]['embedding']

            # 创建用户
            user = User.objects.create_user(
                username=username,
                password=password,
                phone=phone,
                email=email,
            )

            # 更新用户的 face 字段
            relative_face_path = os.path.join('face_images', user.username, res['face_image_filename'])
            user.face = relative_face_path
            user.save()

            Cart.objects.create(user=user)

            # 将 embedding 与用户的 username 绑定，并保存到 CHROMA 数据库中
            save_to_chroma(user.username, embedding)

            # 调用 save_process_record 保存处理记录到数据库
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

            # 自动登录并返回双 token
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

    @staticmethod
    def is_valid_email(email):
        """ 验证 email 格式 """
        email_regex = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
        return re.match(email_regex, email)

    @staticmethod
    def is_valid_phone(phone):
        """ 验证手机号格式，假设为 11 位数字 """
        phone_regex = r'^\d{11}$'
        return re.match(phone_regex, phone)
