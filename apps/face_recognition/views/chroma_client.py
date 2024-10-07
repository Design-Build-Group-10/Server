import os

import cv2
from rest_framework.parsers import MultiPartParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework_simplejwt.authentication import JWTAuthentication

from apps.user.models import User
from common.utils.chroma_client import save_to_chroma, delete_from_chroma
from common.utils.face_process import process_frame, save_process_record, save_face_image
from common.utils.response import success_response, bad_request_response, internal_error_response


class FaceEntryView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser]
    scene = 'face_entry'  # 场景名称，用于保存到不同的文件夹

    def post(self, request, *args, **kwargs):
        # 1. 获取上传的图片文件和 identity（user_id）
        image_file = request.FILES.get('image')
        user_id = request.data.get('identity')

        if not image_file:
            return bad_request_response("No image file provided")

        if not user_id:
            return bad_request_response("No identity (user_id) provided")

        try:
            # 2. 检查 user_id 是否存在于数据库中
            try:
                user = User.objects.get(username=user_id)
            except User.DoesNotExist:
                return bad_request_response(f"No user found with identity '{user_id}'")

            # 3. 保存上传的 face 图像
            face_image_info = save_face_image(self.scene, image_file)
            face_image_path = face_image_info['face_image_path']
            folder = face_image_info['folder']

            # 4. 使用 OpenCV 读取图片文件
            frame = cv2.imread(face_image_path)
            if frame is None:
                return bad_request_response("Invalid image file")

            # 5. 处理图像并提取嵌入信息
            result = process_frame(frame)

            # 判断是否存在多张人脸
            num_faces = len(result['processed_faces'])
            if num_faces == 0:
                return bad_request_response("No face detected in the image")
            elif num_faces > 1:
                return bad_request_response("Multiple faces detected. Please upload an image with only one face.")

            # 假设只处理一张人脸，获取第一个人脸的嵌入
            embedding = result['processed_faces'][0]['embedding']

            # 6. 在保存新的人脸嵌入之前，删除 CHROMA 中该用户的旧人脸数据
            try:
                delete_from_chroma(user_id)
            except KeyError:
                pass  # 如果 CHROMA 中没有该用户的旧人脸数据，则忽略异常

            # 7. 将新的嵌入和 user_id 存储到 CHROMA 数据库
            save_to_chroma(user_id, embedding)

            # 8. 保存处理记录到数据库
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

            # 9. 返回成功响应
            return success_response(message="Face data successfully updated in CHROMA.")

        except Exception as e:
            # 捕获异常并返回错误信息
            return internal_error_response(f"Failed to process and store face data: {str(e)}")


class FaceDeleteView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
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
