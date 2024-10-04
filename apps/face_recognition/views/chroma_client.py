import os
import uuid

import cv2
from django.conf import settings
from rest_framework.parsers import MultiPartParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework_simplejwt.authentication import JWTAuthentication

from apps.face_recognition.algorithm.face_processing import process_frame
from common.utils.chroma_client import save_to_chroma, delete_from_chroma
from common.utils.response import success_response, bad_request_response, internal_error_response


class FaceEntryView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser]

    def post(self, request, *args, **kwargs):
        # 1. 获取上传的图片文件和identity
        image_file = request.FILES.get('image')
        user_id = request.data.get('identity')

        if not image_file:
            return bad_request_response("No image file provided")

        if not user_id:
            return bad_request_response("No identity (user_id) provided")

        try:
            # 2. 创建一个唯一的文件夹来保存上传的文件
            unique_folder = os.path.join(settings.MEDIA_ROOT, str(uuid.uuid4()))
            os.makedirs(unique_folder, exist_ok=True)

            # 3. 将上传的图片保存在该文件夹中
            uploaded_image_path = os.path.join(unique_folder, str(uuid.uuid4()) + ".jpg")
            with open(uploaded_image_path, 'wb+') as destination:
                for chunk in image_file.chunks():
                    destination.write(chunk)

            # 使用 OpenCV 读取图片文件
            frame = cv2.imread(uploaded_image_path)
            if frame is None:
                return bad_request_response("Invalid image file")

            # 4. 处理图像并提取嵌入信息
            result = process_frame(frame)

            # 判断是否存在多张人脸
            num_faces = len(result['processed_faces'])
            if num_faces == 0:
                return bad_request_response("No face detected in the image")
            elif num_faces > 1:
                return bad_request_response("Multiple faces detected. Please upload an image with only one face.")

            # 假设只处理一张人脸，获取第一个人脸的嵌入
            embedding = result['processed_faces'][0]['embedding']

            # 5. 将嵌入和 user_id 存储到 CHROMA 数据库
            save_to_chroma(user_id, embedding)

            # 6. 返回成功响应
            return success_response(message="Face data successfully added to CHROMA.")

        except Exception as e:
            # 捕获异常并返回错误信息
            return internal_error_response(f"Failed to process and store face data: {str(e)}")


class FaceDeleteView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        print(request.data)
        # 1. 获取 identity (user_id) 参数
        user_id = request.data.get('identity')

        if not user_id:
            return bad_request_response("No identity (user_id) provided")

        try:
            # 2. 调用 delete_from_chroma(user_id) 删除人脸数据
            delete_from_chroma(user_id)

            # 3. 返回成功响应
            return success_response(message=f"Face data for user_id '{user_id}' successfully deleted from CHROMA.")

        except KeyError as e:
            # 处理当user_id不存在于数据库中的情况
            return bad_request_response(f"Failed to delete: User ID '{user_id}' does not exist in CHROMA.")

        except Exception as e:
            # 捕获其他异常并返回错误信息
            return internal_error_response(f"Failed to delete face data: {str(e)}")
