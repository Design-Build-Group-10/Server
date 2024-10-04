# face_process.py

import os
from datetime import datetime

import cv2
from django.conf import settings
from rest_framework.parsers import MultiPartParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework_simplejwt.authentication import JWTAuthentication

from apps.face_recognition.algorithm.face_processing import process_frame
from apps.face_recognition.models import FaceProcessingRecord, UnknownFace
from common.utils.response import success_response, bad_request_response


class FaceProcessingView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser]

    def post(self, request, *args, **kwargs):
        # 1. 获取上传的图片文件
        image_file = request.FILES.get('image')
        if not image_file:
            return bad_request_response("No image file provided")

        # 2. 获取当前时间，格式化为文件夹和文件名使用的字符串
        current_time = datetime.now().strftime('%Y%m%d_%H%M%S')

        # 3. 创建一个唯一的文件夹来保存上传的文件和处理后的结果
        unique_folder = os.path.join(settings.MEDIA_ROOT, current_time)
        os.makedirs(unique_folder, exist_ok=True)

        # 4. 将上传的图片保存在该文件夹中
        uploaded_image_path = os.path.join(unique_folder, f"{current_time}.jpg")
        with open(uploaded_image_path, 'wb+') as destination:
            for chunk in image_file.chunks():
                destination.write(chunk)

        # 使用 OpenCV 读取图片文件
        frame = cv2.imread(uploaded_image_path)
        if frame is None:
            return bad_request_response("Invalid image file")

        # 5. 处理图像（使用 process_frame 函数）
        result = process_frame(frame)

        # 6. 保存处理后的图片到该文件夹
        frame_path = os.path.join(unique_folder, 'processed_frame.jpg')
        key_points_image_path = os.path.join(unique_folder, 'key_points_image.jpg')

        cv2.imwrite(frame_path, result['frame'])
        cv2.imwrite(key_points_image_path, result['key_points_image'])

        # 保存未识别的面孔
        unknown_face_paths = []
        for i, face in enumerate(result['unknown_faces']):
            face_path = os.path.join(unique_folder, f'unknown_face_{i}.jpg')
            cv2.imwrite(face_path, face)
            unknown_face_paths.append(face_path)

        def get_media_relative_path(file_path):
            """将文件路径转换为相对于 /media/ 的相对路径"""
            relative_path = os.path.relpath(file_path, settings.MEDIA_ROOT)
            return f"/media/{relative_path}".replace('\\', '/')

        # 7. 将处理结果保存到数据库中
        for face_data in result['processed_faces']:
            record = FaceProcessingRecord.objects.create(
                uploaded_image_path=get_media_relative_path(uploaded_image_path),
                processed_frame_path=get_media_relative_path(frame_path),
                key_points_image_path=get_media_relative_path(key_points_image_path),
                identity=face_data['identity'],
                confidence=face_data['confidence'],
                gender=face_data['gender'],
                age=face_data['age'],
                embedding=face_data['embedding'],
            )

            # 保存 unknown_faces，如果该人脸是未知的
            if face_data['identity'] == 'unknown':
                for i, face_image in enumerate(result['unknown_faces']):
                    unknown_face_path = os.path.join(unique_folder, f'unknown_face_{i}.jpg')
                    cv2.imwrite(unknown_face_path, face_image)
                    UnknownFace.objects.create(
                        record=record,
                        face_image_path=get_media_relative_path(unknown_face_path),
                        embedding=result['unknown_embeddings'][i]
                    )

        # 8. 返回生成文件的路径和人脸数据
        def get_media_url(file_path):
            relative_path = str(os.path.relpath(file_path, settings.MEDIA_ROOT))
            return os.path.join(str(settings.MEDIA_URL).rstrip('/'), relative_path).replace('\\', '/')

        response_data = {
            'uploaded_image': get_media_url(uploaded_image_path),
            'processed_frame': get_media_url(frame_path),
            'key_points_image': get_media_url(key_points_image_path),
            'unknown_faces': [get_media_url(path) for path in unknown_face_paths],
        }

        return success_response(response_data)
