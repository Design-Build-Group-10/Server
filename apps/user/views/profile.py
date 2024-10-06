import os
import uuid

import cv2
from django.db import transaction
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework_simplejwt.authentication import JWTAuthentication

from apps.user.serializers import UserSerializer
from common.utils.chroma_client import save_to_chroma
from common.utils.face_process import process_frame
from common.utils.response import internal_error_response, success_response, bad_request_response
from config import settings


class ProfileView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    @staticmethod
    def get(request):
        try:
            user = request.user
            return success_response(data=UserSerializer(user, many=False).data)
        except Exception as e:
            return internal_error_response(f"Failed to retrieve profile: {str(e)}")


class UserAvatar(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    @transaction.atomic
    def put(self, request):
        user = request.user
        if 'avatar' in request.FILES:
            avatar = request.FILES.get('avatar')
            user.avatar = avatar
            user.save()
            return success_response(data=UserSerializer(user, many=False).data)
        else:
            return bad_request_response("avatar is required")


class UserFace(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    @transaction.atomic
    def put(self, request):
        user = request.user

        # 1. 检查是否上传了face文件
        if 'face' not in request.FILES:
            return bad_request_response("face is required")

        face_image = request.FILES.get('face')

        try:
            # 2. 创建一个唯一的文件夹来保存上传的face图像
            user_folder = os.path.join(str(settings.MEDIA_ROOT), 'face_images', user.username)
            os.makedirs(user_folder, exist_ok=True)

            # 3. 将face图像保存到该文件夹中
            face_image_filename = str(uuid.uuid4()) + ".jpg"
            face_image_path = os.path.join(user_folder, face_image_filename)
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

            # 7. 获取第一个人脸的embedding
            embedding = result['processed_faces'][0]['embedding']

            # 8. 将用户的face字段更新为新上传的图像路径
            relative_face_path = os.path.join('face_images', user.username, face_image_filename)
            user.face = relative_face_path
            user.save()

            # 9. 将embedding与用户的username绑定，并保存到CHROMA数据库中
            save_to_chroma(user.username, embedding)

            # 10. 返回成功响应，包含用户的最新信息
            return success_response(data=UserSerializer(user, many=False).data)

        except Exception as e:
            # 捕获所有异常并返回内部错误响应
            transaction.set_rollback(True)
            return internal_error_response(f"Failed to process face image: {str(e)}")
