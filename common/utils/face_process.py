# -*- coding: utf-8 -*-
"""
File: face_processing.py
Description: Handles all face processing tasks such as detection and drawing.
Author: Wang Zhiwei, Zhao Zheyun
Date: 2024.07.03

Copyright (C) 2024 Wang Zhiwei, Zhao Zheyun. All rights reserved.
Unauthorized copying of this file, via any medium, is strictly prohibited.
Proprietary and confidential.
Contact: wangzw@example.com
"""
import asyncio
import os
import uuid

import cv2
import numpy as np
from asgiref.sync import sync_to_async

from apps.face_recognition.models import FaceProcessingRecord, UnknownFace
from common.utils.chroma_client import face_collection
from common.utils.face_analysis import FaceAnalysis
from config import settings

faceAnalysis = FaceAnalysis(providers=['CUDAExecutionProvider', 'CPUExecutionProvider'])
faceAnalysis.prepare(ctx_id=0, det_size=(640, 640))


def process_frame(frame):
    """
    处理单帧图像以进行人脸识别，识别出的人脸周围绘制框，并且如果识别出身份，则标记身份。

    该函数首先复制帧以保留原始数据，使用预训练的模型检测帧中的人脸，
    然后查询人脸集合数据库以根据面部嵌入找到最接近的匹配身份。
    已知身份的人脸用绿色框高亮显示，并标记身份和置信度分数。
    未知的人脸用红色框标记，标签为“未知”。

    参数：
    - frame (numpy.ndarray)：待处理的视频帧。

    返回值：
    - dict：一个字典，包含：
      - 'frame': 带有每个检测到的人脸的绘制注释的原始帧。
      - 'key_points_image': 与输入帧相同尺寸的白板图像，显示检测到的人脸和注释。
      - 'unknown_faces': 一个列表，包含未被识别的人脸图像（numpy数组）。
      - 'unknown_embeddings': 一个列表，包含对应于未知人脸的嵌入，用于进一步处理或存储。

    该函数使用全局实例，如 `faceAnalysis` 和 `face_collection`，调用此函数前应先初始化这些实例。
    """

    original_frame = frame.copy()
    faces = faceAnalysis.get(frame)

    key_points_image = np.ones_like(frame) * 255
    key_points_image = faceAnalysis.draw_on(key_points_image, faces)

    processed_faces = []
    unknown_faces = []
    unknown_embeddings = []

    for face in faces:
        bbox = face.bbox.astype(int)
        embedding = face.normed_embedding.tolist()
        min_dist = float('inf')
        identity = 'unknown'
        confidence = 0

        gender = 'Male' if face.gender == 1 else 'Female'
        age = face.age

        results = face_collection.query(query_embeddings=[embedding], n_results=1)
        if results['ids'] and results['ids'][0]:
            nearest_id = results['ids'][0][0]
            min_dist = results['distances'][0][0]
            if min_dist < 1.0:
                identity = nearest_id
                confidence = min(1 - min_dist, 1)

        color = (0, 0, 255)
        if confidence > 0.5:
            color = (0, 255, 0)
        elif confidence > 0.3:
            color = (0, 255, 255)

        # 收集处理后的信息
        face_data = {
            'identity': identity,
            'confidence': confidence,
            'gender': gender,
            'age': int(age),
            'embedding': embedding
        }
        processed_faces.append(face_data)

        if identity == 'unknown':
            face_image = original_frame[bbox[1]:bbox[3], bbox[0]:bbox[2]]
            unknown_faces.append(face_image)
            unknown_embeddings.append(embedding)

        cv2.rectangle(frame, (bbox[0], bbox[1]), (bbox[2], bbox[3]), color, 2)
        cv2.putText(frame, f'ID: {identity} ({confidence:.2f})', (bbox[0], bbox[1] - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.9,
                    color, 2)
        cv2.putText(frame, f'Gender: {gender}, Age: {int(age)}', (bbox[0], bbox[3] + 20), cv2.FONT_HERSHEY_SIMPLEX, 0.7,
                    color, 2)

    return {
        'frame': frame,
        'key_points_image': key_points_image,
        'processed_faces': processed_faces,
        'unknown_faces': unknown_faces,
        'unknown_embeddings': unknown_embeddings
    }


def save_face_image(scene, face_image):
    """
    登录时进行的人脸识别保存到login文件夹，注册时进行的人脸识别保存到register文件夹，机器人上传的图片人脸识别后保存到robot文件夹。
    :param scene:
    :param face_image:
    :return:
    """
    from datetime import datetime

    current_time = datetime.now().strftime('%Y%m%d_%H%M%S')

    folder = os.path.join(str(settings.MEDIA_ROOT), 'face_processing', scene, current_time)
    os.makedirs(folder, exist_ok=True)

    face_image_filename = str(uuid.uuid4()) + ".jpg"
    face_image_path = os.path.join(folder, face_image_filename)
    with open(face_image_path, 'wb+') as destination:
        for chunk in face_image.chunks():
            destination.write(chunk)

    return {
        'folder': folder,
        'face_image_filename': face_image_filename,
        'face_image_path': face_image_path
    }


# 用于处理同步阻塞的操作，例如 cv2.imwrite
async def async_write_image(file_path, image):
    await asyncio.to_thread(cv2.imwrite, file_path, image)


@sync_to_async
def save_face_record(record_data):
    return FaceProcessingRecord.objects.create(**record_data)


@sync_to_async
def save_unknown_face(record, unknown_face_data):
    UnknownFace.objects.create(record=record, **unknown_face_data)


def get_media_relative_path(file_path):
    """将文件路径转换为相对于 /media/ 的相对路径"""
    relative_path = os.path.relpath(file_path, settings.MEDIA_ROOT)
    return f"/media/{relative_path}".replace('\\', '/')


async def save_process_record(folder, face_image_path, frame_path, key_points_image_path, result):
    """
    异步保存人脸处理记录到数据库中，包括识别和未识别的情况
    :param folder:
    :param face_image_path:
    :param frame_path:
    :param key_points_image_path:
    :param result:
    :return:
    """

    # 遍历每个已处理的人脸
    for face_data in result['processed_faces']:
        # 创建记录
        record_data = {
            'uploaded_image_path': get_media_relative_path(face_image_path),
            'processed_frame_path': get_media_relative_path(frame_path),
            'key_points_image_path': get_media_relative_path(key_points_image_path),
            'identity': face_data['identity'],
            'confidence': face_data['confidence'],
            'gender': face_data['gender'],
            'age': face_data['age'],
            'embedding': face_data['embedding'],
        }

        # 使用异步 ORM 创建 FaceProcessingRecord
        record = await save_face_record(record_data)

        # 如果身份是未知的，保存未知人脸
        if face_data['identity'] == 'unknown':
            for i, face_image in enumerate(result['unknown_faces']):
                unknown_face_path = os.path.join(folder, f'unknown_face_{i}.jpg')

                # 异步保存图片文件
                await async_write_image(unknown_face_path, face_image)

                # 创建未知人脸记录
                unknown_face_data = {
                    'face_image_path': get_media_relative_path(unknown_face_path),
                    'embedding': result['unknown_embeddings'][i]
                }

                # 使用异步 ORM 创建 UnknownFace
                await save_unknown_face(record, unknown_face_data)
