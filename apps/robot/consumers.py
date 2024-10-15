import json
from datetime import timedelta

import cv2
import numpy as np
from asgiref.sync import sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer
from django.utils import timezone


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
        try:
            print("Receiving data...")
            # 确保是二进制数据传输
            if not bytes_data:
                print("No binary data received.")
                await self.send_json({"error": "No binary data received"})
                return

            print("Binary data received, processing image...")

            # 将二进制数据读入 OpenCV
            np_arr = np.frombuffer(bytes_data, np.uint8)
            frame = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)
            if frame is None:
                print("Invalid image file, cannot read.")
                await self.send_json({"error": "Invalid image file"})
                return

            print("Image successfully loaded, processing with OpenCV...")

            # 处理图像
            from common.utils.face_process import simple_process_frame, save_face_image, save_process_record

            result = simple_process_frame(frame)

            # 获取所有处理后的面部图像列表
            processed_faces = result['frame']

            user_info = result['processed_faces']

            await self.handlePoints(user_info)

            # 将处理后的图像转为二进制格式
            ret, buffer = cv2.imencode('.jpg', processed_faces)
            if not ret:
                print("Failed to encode image.")
                await self.send_json({"error": "Failed to encode image"})
                return

            # 将处理后的二进制图像数据发送到房间组
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'send_image',
                    'image_data': buffer.tobytes(),
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
        # 将二进制图像数据直接发送给客户端
        await self.send(bytes_data=event['image_data'])

    @sync_to_async
    def handlePoints(self, user_info):
        from apps.user.models import User, Message

        # 遍历处理后的脸部数据
        for face_data in user_info:
            identity = face_data.get('identity')

            # 如果身份不是 'unknown'，则尝试从数据库中获取用户
            if identity != 'unknown':
                try:
                    # 查找与身份匹配的用户
                    user = User.objects.get(username=identity)

                    # 获取当前时间
                    now = timezone.now()

                    # 检查距离上一次检测时间是否超过10分钟
                    if user.last_detected is None or (now - user.last_detected) > timedelta(minutes=10):
                        # 增加用户积分
                        user.points += 5
                        # 更新 last_detected 为当前时间
                        user.last_detected = now
                        # 保存用户数据
                        user.save()

                        # 向用户发送一条消息
                        Message.objects.create(
                            user=user,
                            title="Robot Detect Reward",
                            description="🎉 You have received 5 reward points for being detected by robot.",
                            created_at=now
                        )

                except User.DoesNotExist:
                    print(f"User with username '{identity}' not found")


class TransmitConsumer(AsyncWebsocketConsumer):
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
        try:
            print("Receiving data...")
            # 确保是二进制数据传输
            if not bytes_data:
                print("No binary data received.")
                await self.send_json({"error": "No binary data received"})
                return

            print("Binary data received, processing image...")

            # image_file = ContentFile(bytes_data)

            # 4. 将二进制图像数据发送到房间组
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'send_image',
                    'image_data': bytes_data,
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
        # 将二进制图像数据直接发送给客户端
        await self.send(bytes_data=event['image_data'])
