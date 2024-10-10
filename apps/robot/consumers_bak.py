import json
import os
import uuid

import cv2
from asgiref.sync import sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer
from django.core.files.base import ContentFile


class CameraConsumer(AsyncWebsocketConsumer):
    def __init__(self, *args, **kwargs):
        super().__init__(args, kwargs)
        self.robot = None
        self.serial_number = None
        self.room_group_name = None

    async def connect(self):
        from apps.user.models import Robot
        # 1. 检查是否提供了 serial_number
        serial_number = self.scope['url_route']['kwargs'].get('serial_number')
        if not serial_number:
            print("No serial_number provided, closing connection.")
            await self.close()
            return

        print(f"Connecting with serial_number: {serial_number}")

        # 2. 查询 serial_number 对应的机器人
        try:
            self.robot = await sync_to_async(Robot.objects.get)(serial_number=serial_number)
            print(f"Robot found: {self.robot.name}")
        except Robot.DoesNotExist:
            print(f"Robot with serial_number {serial_number} does not exist, closing connection.")
            await self.close()
            return

        # 设置房间组名为机器人 serial_number
        self.serial_number = serial_number
        self.room_group_name = f"robot_{self.serial_number}"
        print(f"Room group name set to: {self.room_group_name}")

        # 3. 将用户加入房间组
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        print(f"User added to group: {self.room_group_name}")

        await self.accept()
        print("Connection accepted.")

    async def disconnect(self, close_code):
        # 离开房间组
        print(f"Disconnecting from group: {self.room_group_name}")
        if self.room_group_name:
            await self.channel_layer.group_discard(
                self.room_group_name,
                self.channel_name
            )
        print("Disconnected.")

    async def receive(self, text_data=None, bytes_data=None):
        from config import settings
        try:
            print("Receiving data...")
            # 确保是二进制数据传输
            if not bytes_data:
                print("No binary data received.")
                await self.send_json({"error": "No binary data received"})
                return

            print("Binary data received, processing image...")

            # 1. 处理接收到的二进制图片数据
            image_filename = f"{uuid.uuid4()}.jpg"
            image_path = os.path.join(settings.MEDIA_ROOT, 'ws_images', image_filename)
            os.makedirs(os.path.dirname(image_path), exist_ok=True)

            image_file = ContentFile(bytes_data)

            # 保存二进制图片数据到文件
            with open(image_path, 'wb+') as destination:
                for chunk in image_file.chunks():
                    destination.write(chunk)

            print(f"Image saved to: {image_path}")

            # 2. 使用 OpenCV 读取图片文件
            frame = cv2.imread(image_path)
            if frame is None:
                print("Invalid image file, cannot read.")
                await self.send_json({"error": "Invalid image file"})
                return

            print("Image successfully loaded, processing with OpenCV...")

            # 3. 处理图像
            from common.utils.face_process import process_frame, save_face_image, save_process_record

            result = process_frame(frame)
            # print(f"Face processing result: {result}")

            # 检查人脸数量
            num_faces = len(result['processed_faces'])
            if num_faces == 0:
                print("No face detected in the image.")
                await self.send_json({"error": "No face detected in the image"})
                return
            elif num_faces > 1:
                print("Multiple faces detected.")
                await self.send_json({"error": "Multiple faces detected. Please upload an image with only one face."})
                return

            # print("Face detected, proceeding to save image...")

            # 4. 保存 face 图像和处理记录
            # face_image_info = save_face_image('camera_ws', image_file)
            # folder = face_image_info['folder']
            # face_image_path = face_image_info['face_image_path']

            # frame_path = os.path.join(folder, 'processed_frame.jpg')
            # key_points_image_path = os.path.join(folder, 'key_points_image.jpg')

            # cv2.imwrite(frame_path, result['frame'])
            # cv2.imwrite(key_points_image_path, result['key_points_image'])
            #
            # print(f"Processed frame saved at: {frame_path}")
            # print(f"Key points image saved at: {key_points_image_path}")

            # await save_process_record(
            #     folder=folder,
            #     face_image_path=face_image_path,
            #     frame_path=frame_path,
            #     key_points_image_path=key_points_image_path,
            #     result=result
            # )
            print("Process record saved.")

            # 转换绝对路径为相对路径
            # def get_media_relative_path(file_path):
            #     relative_path = os.path.relpath(file_path, settings.MEDIA_ROOT)
            #     return f"{settings.MEDIA_URL}{relative_path}".replace('\\', '/')

            # 5. 返回处理后的结果
            response_data = {
                "message": "Image processed successfully",
                # "uploaded_image": get_media_relative_path(face_image_info['face_image_path']),
                # "processed_frame": get_media_relative_path(frame_path),
                # "key_points_image": get_media_relative_path(key_points_image_path),
            }

            print(f"Sending processed data: {response_data}")

            # 6. 将处理后的图像发送到房间内的所有用户
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'send_image',
                    'processed_data': response_data,
                }
            )
        except Exception as e:
            print(f"Error during image processing: {str(e)}")
            await self.send_json({"error": f"Failed to process image: {str(e)}"})

    async def send_json(self, data):
        print(f"Sending JSON data: {data}")
        await self.send(text_data=json.dumps(data))

    async def send_image(self, event):
        print(f"Sending image data to room: {self.room_group_name}")
        # 向房间内的所有连接发送图像数据
        await self.send(text_data=json.dumps({
            'processed_data': event['processed_data']
        }))
