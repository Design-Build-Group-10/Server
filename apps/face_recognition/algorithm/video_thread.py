# -*- coding: utf-8 -*-
"""
File: video_thread.py
Description: Manages video capture and frame processing in a separate thread.
Author: Wang Zhiwei, Zhao Zheyun
Date: 2024.07.03

Copyright (C) 2024 Wang Zhiwei, Zhao Zheyun. All rights reserved.
Unauthorized copying of this file, via any medium, is strictly prohibited.
Proprietary and confidential.
Contact: zhaozy@example.com
"""

import time

import cv2
import numpy as np
from PyQt5.QtCore import QThread, pyqtSignal

from .face_processing import process_frame


class VideoThread(QThread):
    change_pixmap_signal = pyqtSignal(str, np.ndarray, np.ndarray, list, list)
    fps_signal = pyqtSignal(float)

    def __init__(self):
        super().__init__()
        self._run_flag = True
        self.frame_count = 0
        self.start_time = time.time()

    def run(self):
        cap = cv2.VideoCapture(0)
        if not cap.isOpened():
            self._run_flag = False
            print("Error: Could not open video.")
            return

        while self._run_flag:
            ret, frame = cap.read()
            if not ret:
                break

            result = process_frame(frame)
            processed_frame = result['frame']
            whiteboard = result['whiteboard']
            unknown_faces = result['unknown_faces']
            unknown_embeddings = result['unknown_embeddings']

            self.change_pixmap_signal.emit("camera", processed_frame, whiteboard, unknown_faces, unknown_embeddings)
            self.frame_count += 1
            elapsed_time = time.time() - self.start_time
            if elapsed_time >= 1.0:
                fps = self.frame_count / elapsed_time
                self.fps_signal.emit(fps)  # 发送帧率信号
                self.frame_count = 0
                self.start_time = time.time()

        cap.release()

    def stop(self):
        self._run_flag = False
        self.wait()
