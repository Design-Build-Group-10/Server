import base64
import json
import os
import uuid

import cv2
from channels.generic.websocket import AsyncWebsocketConsumer
from django.conf import settings
from django.core.files.base import ContentFile


class CameraConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.accept()

    async def disconnect(self, close_code):
        pass

    async def receive(self, text_data=None, bytes_data=None):
        try:
            if not text_data:
                await self.send_json({"error": "No data received"})
                return

            # 解析 JSON 数据
            data = json.loads(text_data)
            base64_image = data.get('image')

            if not base64_image:
                await self.send_json({"error": "No image data provided"})
                return

            # 1. 解码 Base64 图片
            image_data = base64.b64decode(base64_image)
            image_filename = f"{uuid.uuid4()}.jpg"
            image_path = os.path.join(settings.MEDIA_ROOT, 'ws_images', image_filename)
            os.makedirs(os.path.dirname(image_path), exist_ok=True)

            image_file = ContentFile(image_data)

            # 保存解码后的图片到服务器
            with open(image_path, 'wb+') as destination:
                for chunk in image_file.chunks():
                    destination.write(chunk)

            # 2. 使用 OpenCV 读取图片文件
            frame = cv2.imread(image_path)
            if frame is None:
                await self.send_json({"error": "Invalid image file"})
                return

            # 3. 处理图像
            from common.utils.face_process import process_frame, save_face_image, save_process_record

            result = process_frame(frame)

            # 检查人脸数量
            num_faces = len(result['processed_faces'])
            if num_faces == 0:
                await self.send_json({"error": "No face detected in the image"})
                return
            elif num_faces > 1:
                await self.send_json({"error": "Multiple faces detected. Please upload an image with only one face."})
                return

            # 4. 保存 face 图像和处理记录
            face_image_info = save_face_image('camera_ws', image_file)
            folder = face_image_info['folder']
            face_image_path = face_image_info['face_image_path']

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

            # 转换绝对路径为相对路径
            def get_media_relative_path(file_path):
                relative_path = os.path.relpath(file_path, settings.MEDIA_ROOT)
                return f"{settings.MEDIA_URL}{relative_path}".replace('\\', '/')

            # 5. 返回处理后的结果
            response_data = {
                "message": "Image processed successfully",
                "uploaded_image": get_media_relative_path(face_image_info['face_image_path']),
                "processed_frame": get_media_relative_path(frame_path),
                "key_points_image": get_media_relative_path(key_points_image_path),
            }

            await self.send_json(response_data)

        except Exception as e:
            await self.send_json({"error": f"Failed to process image: {str(e)}"})

    async def send_json(self, data):
        await self.send(text_data=json.dumps(data))
