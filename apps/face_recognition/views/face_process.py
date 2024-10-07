# face_process.py

import os

import cv2
from django.conf import settings
from rest_framework.parsers import MultiPartParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework_simplejwt.authentication import JWTAuthentication

from common.utils.face_process import process_frame, save_process_record, save_face_image
from common.utils.response import success_response, bad_request_response


class FaceProcessingView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser]
    scene = 'robot'

    def post(self, request, *args, **kwargs):
        # 1. 获取上传的图片文件
        image_file = request.FILES.get('image')
        if not image_file:
            return bad_request_response("No image file provided")

        # 2. 使用 save_face_image 保存上传的图片到相应的目录
        res = save_face_image(self.scene, image_file)
        face_image_path = res['face_image_path']
        folder = res['folder']

        # 3. 使用 OpenCV 读取图片文件
        frame = cv2.imread(face_image_path)
        if frame is None:
            return bad_request_response("Invalid image file")

        # 4. 处理图像（使用 process_frame 函数）
        result = process_frame(frame)

        # 5. 保存处理后的图片到相应的目录
        frame_path = os.path.join(folder, 'processed_frame.jpg')
        key_points_image_path = os.path.join(folder, 'key_points_image.jpg')

        cv2.imwrite(frame_path, result['frame'])
        cv2.imwrite(key_points_image_path, result['key_points_image'])

        # 6. 调用 save_process_record 函数，保存处理记录到数据库
        save_process_record(
            folder=folder,
            face_image_path=face_image_path,
            frame_path=frame_path,
            key_points_image_path=key_points_image_path,
            result=result
        )

        # 7. 返回生成文件的路径和人脸数据
        def get_media_url(file_path):
            relative_path = str(os.path.relpath(file_path, settings.MEDIA_ROOT))
            return os.path.join(str(settings.MEDIA_URL).rstrip('/'), relative_path).replace('\\', '/')

        response_data = {
            'uploaded_image': get_media_url(face_image_path),
            'processed_frame': get_media_url(frame_path),
            'key_points_image': get_media_url(key_points_image_path),
            'unknown_faces': [
                get_media_url(os.path.join(folder, f'unknown_face_{i}.jpg')) for i in
                range(len(result['unknown_faces']))
            ],
        }

        return success_response(response_data)
