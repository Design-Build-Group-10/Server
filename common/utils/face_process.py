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

import cv2
import numpy as np

from common.utils.chroma_client import face_collection
from common.utils.face_analysis import FaceAnalysis

# 确保只实例化一次
faceAnalysis = None


def get_face_analysis():
    global faceAnalysis
    if faceAnalysis is None:
        faceAnalysis = FaceAnalysis(providers=['CUDAExecutionProvider', 'CPUExecutionProvider'])
        faceAnalysis.prepare(ctx_id=0, det_size=(640, 640))
    return faceAnalysis


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
    faces = get_face_analysis().get(frame)

    key_points_image = np.ones_like(frame) * 255
    key_points_image = get_face_analysis().draw_on(key_points_image, faces)

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
