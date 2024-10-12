import os

import cv2
from django.db import transaction
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework_simplejwt.authentication import JWTAuthentication

from apps.user.serializers import UserSerializer
from common.utils.chroma_client import save_to_chroma
from common.utils.face_process import process_frame, save_process_record, save_face_image
from common.utils.response import internal_error_response, success_response, bad_request_response


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
    scene = 'user_face'  # 场景名称，用于保存到不同的文件夹

    @transaction.atomic
    async def put(self, request):
        user = request.user

        # 1. 检查是否上传了 face 文件
        if 'face' not in request.FILES:
            return bad_request_response("face is required")

        face_image = request.FILES.get('face')

        try:
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

            # 6. 获取第一个人脸的 embedding
            embedding = result['processed_faces'][0]['embedding']

            # 7. 更新用户的 face 字段
            relative_face_path = os.path.join('face_images', user.username, face_image_info['face_image_filename'])
            user.face = relative_face_path
            user.save()

            # 8. 将 embedding 与用户的 username 绑定，并保存到 CHROMA 数据库中
            save_to_chroma(user.username, embedding)

            # 9. 保存处理记录到数据库
            frame_path = os.path.join(folder, 'processed_frame.jpg')
            key_points_image_path = os.path.join(folder, 'key_points_image.jpg')
            cv2.imwrite(frame_path, result['frame'])
            cv2.imwrite(key_points_image_path, result['key_points_image'])

            await save_process_record(
                folder=folder,
                face_image_path=face_image_path,
                frame_path=frame_path,
                key_points_image_path=key_points_image_path,
                result=result
            )

            # 10. 返回成功响应，包含用户的最新信息
            return success_response(data=UserSerializer(user, many=False).data)

        except Exception as e:
            # 捕获所有异常并返回内部错误响应
            transaction.set_rollback(True)
            return internal_error_response(f"Failed to process face image: {str(e)}")
