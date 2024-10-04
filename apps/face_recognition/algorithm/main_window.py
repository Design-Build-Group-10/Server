# -*- coding: utf-8 -*-
"""
File: main_window.py
Description: Contains the main window class for the face recognition application.
Author: Wang Zhiwei, Zhao Zheyun
Date: 2024.07.03

Copyright (C) 2024 Wang Zhiwei, Zhao Zheyun. All rights reserved.
This file is part of a face recognition project. Unauthorized copying of this file, via any medium, is strictly prohibited.
Proprietary and confidential.
Contact: wangzw@example.com
"""

import os
import sys

import cv2
import numpy as np
from PyQt5.QtCore import Qt, QUrl
from PyQt5.QtGui import QImage, QPixmap, QIcon
from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent
from PyQt5.QtMultimediaWidgets import QVideoWidget
from PyQt5.QtWidgets import (QApplication, QMainWindow, QLabel, QVBoxLayout,
                             QWidget, QPushButton, QLineEdit, QMessageBox, QHBoxLayout, QSplitter,
                             QTabWidget, QFileDialog, QScrollArea, QProgressDialog)

from chroma_client import face_collection, save_to_chroma
from face_processing import process_frame
from video_thread import VideoThread


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("人脸识别系统")
        self.setGeometry(100, 100, 1600, 900)
        self.setWindowIcon(QIcon('icon.jpg'))
        self.initUI()

    def initUI(self):
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        self.main_layout = QVBoxLayout(self.central_widget)
        self.main_layout.setContentsMargins(10, 10, 10, 10)
        self.main_layout.setSpacing(10)

        # TabBar for different functionalities
        self.tabs = QTabWidget()
        self.main_layout.addWidget(self.tabs)
        self.tabs.currentChanged.connect(self.on_tab_change)

        self.create_camera_recognition_tab()
        self.create_face_entry_tab()
        self.create_video_recognition_tab()
        self.create_face_delete_tab()

    def create_face_entry_tab(self):
        self.face_entry_tab = QWidget()
        self.tabs.addTab(self.face_entry_tab, "图片人脸识别")

        layout = QVBoxLayout()

        self.splitter = QSplitter(Qt.Horizontal)

        self.left_image_label = QLabel("Upload Image")
        self.left_image_label.setMinimumSize(400, 600)
        self.left_image_label.setAlignment(Qt.AlignCenter)
        self.left_image_label.setStyleSheet("QLabel { background-color : lightgray; }")

        self.middle_image_label = QLabel("Label Image")
        self.middle_image_label.setMinimumSize(400, 600)
        self.middle_image_label.setAlignment(Qt.AlignCenter)
        self.middle_image_label.setStyleSheet("QLabel { background-color : lightgray; }")

        self.right_image_label = QLabel("3D Face Image")
        self.right_image_label.setMinimumSize(400, 600)
        self.right_image_label.setAlignment(Qt.AlignCenter)
        self.right_image_label.setStyleSheet("QLabel { background-color : lightgray; }")

        self.splitter.addWidget(self.left_image_label)
        self.splitter.addWidget(self.middle_image_label)
        self.splitter.addWidget(self.right_image_label)
        self.splitter.setStretchFactor(0, 1)
        self.splitter.setStretchFactor(1, 1)
        self.splitter.setStretchFactor(2, 1)

        upload_button = QPushButton("上传图片")
        upload_button.clicked.connect(lambda _,: self.upload_image())

        layout.addWidget(self.splitter)
        layout.addWidget(upload_button, alignment=Qt.AlignCenter)

        self.entry_unknown_faces_layout = QHBoxLayout()

        scroll_area = QScrollArea()
        scroll_widget = QWidget()
        scroll_widget.setLayout(self.entry_unknown_faces_layout)
        scroll_area.setWidget(scroll_widget)
        scroll_area.setWidgetResizable(True)
        scroll_area.setFixedHeight(300)

        layout.addWidget(scroll_area)

        self.face_entry_tab.setLayout(layout)

    def create_face_delete_tab(self):
        self.face_delete_tab = QWidget()
        self.tabs.addTab(self.face_delete_tab, "人脸信息删除")

        layout = QVBoxLayout()
        layout.setSpacing(10)

        self.delete_id_input = QLineEdit()
        self.delete_id_input.setPlaceholderText("输入要删除的人脸ID")
        self.delete_id_input.setFixedSize(300, 40)

        delete_button = QPushButton("删除人脸信息")
        delete_button.clicked.connect(self.delete_face_info)

        layout.addWidget(self.delete_id_input, alignment=Qt.AlignCenter)
        layout.addWidget(delete_button, alignment=Qt.AlignCenter)

        self.face_delete_tab.setLayout(layout)

    def create_video_recognition_tab(self):
        self.video_recognition_tab = QWidget()
        self.tabs.addTab(self.video_recognition_tab, "视频人脸识别")

        layout = QVBoxLayout()

        self.splitter = QSplitter(Qt.Horizontal)

        self.left_video_player = QMediaPlayer(None, QMediaPlayer.VideoSurface)
        self.middle_video_player = QMediaPlayer(None, QMediaPlayer.VideoSurface)
        self.right_video_player = QMediaPlayer(None, QMediaPlayer.VideoSurface)

        self.left_video_widget = QVideoWidget()
        self.middle_video_widget = QVideoWidget()
        self.right_video_widget = QVideoWidget()

        self.left_video_widget.setMinimumSize(400, 600)
        self.middle_video_widget.setMinimumSize(400, 600)
        self.right_video_widget.setMinimumSize(400, 600)

        self.left_video_player.setVideoOutput(self.left_video_widget)
        self.middle_video_player.setVideoOutput(self.middle_video_widget)
        self.right_video_player.setVideoOutput(self.right_video_widget)

        # 添加到分隔器
        self.splitter.addWidget(self.left_video_widget)
        self.splitter.addWidget(self.middle_video_widget)
        self.splitter.addWidget(self.right_video_widget)
        self.splitter.setStretchFactor(0, 1)
        self.splitter.setStretchFactor(1, 1)
        self.splitter.setStretchFactor(2, 1)

        self.setup_video_players()

        button_layout = QHBoxLayout()

        self.upload_button = QPushButton("上传视频")
        self.upload_button.clicked.connect(self.upload_video)

        self.clear_video_button = QPushButton("清除视频")
        self.clear_video_button.clicked.connect(self.clear_video)

        self.start_video_button = QPushButton("播放视频")
        self.start_video_button.clicked.connect(self.start_all_players)

        self.stop_video_button = QPushButton("暂停视频")
        self.stop_video_button.clicked.connect(self.stop_all_players)

        button_layout.addWidget(self.upload_button)
        button_layout.addWidget(self.clear_video_button)
        button_layout.addWidget(self.start_video_button)
        button_layout.addWidget(self.stop_video_button)

        layout.addWidget(self.splitter)
        layout.addLayout(button_layout)

        self.video_recognition_tab.setLayout(layout)

    def create_camera_recognition_tab(self):
        self.camera_recognition_tab = QWidget()
        self.tabs.addTab(self.camera_recognition_tab, "摄像头人脸识别")

        layout = QVBoxLayout()

        self.splitter = QSplitter(Qt.Horizontal)

        self.processed_label = QLabel(self)
        self.processed_label.setMinimumSize(800, 600)
        self.processed_label.setAlignment(Qt.AlignCenter)
        self.processed_label.setStyleSheet("QLabel { background-color : lightgray; border: 1px solid black; }")

        self.whiteboard_label = QLabel(self)
        self.whiteboard_label.setMinimumSize(800, 600)
        self.whiteboard_label.setAlignment(Qt.AlignCenter)
        self.whiteboard_label.setStyleSheet("QLabel { background-color : lightgray; border: 1px solid black; }")

        self.splitter.addWidget(self.processed_label)
        self.splitter.addWidget(self.whiteboard_label)
        self.splitter.setStretchFactor(0, 1)
        self.splitter.setStretchFactor(1, 1)

        layout.addWidget(self.splitter)

        self.camera_unknown_faces_layout = QHBoxLayout()

        scroll_area = QScrollArea()
        scroll_widget = QWidget()
        scroll_widget.setLayout(self.camera_unknown_faces_layout)
        scroll_area.setWidget(scroll_widget)
        scroll_area.setWidgetResizable(True)
        scroll_area.setFixedHeight(300)

        layout.addWidget(scroll_area)

        self.fps_label = QLabel("FPS: 0.00")  # 添加帧率标签
        self.fps_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.fps_label, alignment=Qt.AlignCenter)  # 添加帧率标签到布局

        self.camera_recognition_tab.setLayout(layout)

    def display_image(self, label, img, width, height):
        qt_img = self.convert_cv_qt(img)
        label.setPixmap(qt_img.scaled(width, height, Qt.KeepAspectRatio, Qt.SmoothTransformation))

    def upload_image(self):
        options = QFileDialog.Options()
        file_name, _ = QFileDialog.getOpenFileName(self, "选择图片文件", "",
                                                   "Images (*.png *.jpg *.bmp);;All Files (*)", options=options)
        if file_name:
            self.image = cv2.imread(file_name)
            self.display_image(self.left_image_label, self.image, self.left_image_label.width(),
                               self.left_image_label.height())
            frame = self.image.copy()

            result = process_frame(frame)
            processed_frame = result['frame']
            whiteboard = result['whiteboard']
            unknown_faces = result['unknown_faces']
            unknown_embeddings = result['unknown_embeddings']
            self.display_image(self.middle_image_label, processed_frame, self.middle_image_label.width(),
                               self.middle_image_label.height())
            self.display_image(self.right_image_label, whiteboard, self.right_image_label.width(),
                               self.right_image_label.height())
            self.update_images("entry", processed_frame, whiteboard, unknown_faces, unknown_embeddings)

    def upload_video(self):
        # 打开文件选择对话框，让用户选择视频文件
        video_file, _ = QFileDialog.getOpenFileName(self.video_recognition_tab, "选择视频文件", "",
                                                    "视频文件 (*.mp4 *.avi *.mov)")
        # 检查用户是否选择了文件
        if video_file:
            # 显示处理中的状态
            self.progress_dialog = QProgressDialog("正在处理视频...", "取消", 0, 100, self.video_recognition_tab)
            self.progress_dialog.setWindowModality(Qt.WindowModal)
            self.progress_dialog.setMinimumDuration(0)  # 立即显示对话框

            # 加载并播放视频
            self.left_video_player.setMedia(QMediaContent(QUrl.fromLocalFile(video_file)))
            self.left_video_player.play()

            self.process_video(video_file)

    def process_video(self, video_file):
        # 打开输入视频
        cap = cv2.VideoCapture(video_file)
        if not cap.isOpened():
            print("Error: Unable to open video file.")
            return

        # 获取视频帧率和尺寸
        fps = cap.get(cv2.CAP_PROP_FPS)
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

        # 设置输出视频
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')  # 设置视频编解码器
        label_video_out = cv2.VideoWriter('processed_video/processed_video.mp4', fourcc, fps, (width, height))
        whiteboard_video_out = cv2.VideoWriter('processed_video/whiteboard_video.mp4', fourcc, fps, (width, height))

        # 用于进度条更新
        self.progress_dialog.setMaximum(frame_count)

        current_frame = 0
        while True:
            ret, frame = cap.read()
            if not ret:
                break

            # 处理视频帧
            result = process_frame(frame)
            processed_frame = result['frame']
            whiteboard = result['whiteboard']

            # 写入处理后的帧到输出视频
            label_video_out.write(processed_frame)
            whiteboard_video_out.write(whiteboard)

            # 更新进度条
            progress_percentage = int((current_frame / frame_count) * 100)
            self.progress_dialog.setLabelText(f"Processing frames... ({progress_percentage}%)")
            self.progress_dialog.setValue(current_frame)
            if self.progress_dialog.wasCanceled():
                print("Processing was canceled by user.")
                break

            current_frame += 1
            print(f"Processed frame {current_frame}/{frame_count}")

        # 清理资源
        cap.release()
        label_video_out.release()
        whiteboard_video_out.release()
        self.progress_dialog.setValue(frame_count)  # 完成处理
        self.progress_dialog.close()

        # 显示处理后的视频
        processed_video_path = os.path.abspath('processed_video/processed_video.mp4')
        whiteboard_video_path = os.path.abspath('processed_video/whiteboard_video.mp4')

        self.middle_video_player.setMedia(QMediaContent(QUrl.fromLocalFile(processed_video_path)))
        self.right_video_player.setMedia(QMediaContent(QUrl.fromLocalFile(whiteboard_video_path)))

        self.left_video_player.stop()
        self.start_all_players()

    def clear_video(self):
        self.left_video_player.stop()
        self.left_video_player.setMedia(QMediaContent())
        self.left_video_widget.update()

        self.middle_video_player.stop()
        self.middle_video_player.setMedia(QMediaContent())
        self.middle_video_widget.update()

        self.right_video_player.stop()
        self.right_video_player.setMedia(QMediaContent())
        self.right_video_widget.update()

    def start_all_players(self):
        self.left_video_player.play()
        self.left_video_widget.update()

        self.middle_video_player.play()
        self.middle_video_widget.update()

        self.right_video_player.play()
        self.right_video_widget.update()

    def stop_all_players(self):
        self.left_video_player.pause()
        self.middle_video_player.pause()
        self.right_video_player.pause()

    def setup_video_players(self):
        self.setup_video_player(self.left_video_player)
        self.setup_video_player(self.middle_video_player)
        self.setup_video_player(self.right_video_player)

    def setup_video_player(self, player):
        player.mediaStatusChanged.connect(lambda status, p=player: self.loop_video(p, status))

    def loop_video(self, player, status):
        if status == QMediaPlayer.EndOfMedia:
            player.play()

    def update_fps(self, fps):
        self.fps_label.setText(f"FPS: {fps:.2f}")

    def update_images(self, tab, processed_frame, whiteboard, unknown_faces, unknown_embeddings):
        containers = []
        if tab == "entry":
            self.remove_all_widget(self.entry_unknown_faces_layout)
            self.process_unknown_faces(tab, containers, unknown_faces, unknown_embeddings)
        elif tab == "camera":
            self.display_image(self.processed_label, processed_frame, self.processed_label.width(),
                               self.processed_label.height())
            self.display_image(self.whiteboard_label, whiteboard, self.whiteboard_label.width(),
                               self.whiteboard_label.height())
            if self.unknown_faces_requested:
                self.unknown_faces_requested = False
                self.remove_all_widget(self.camera_unknown_faces_layout)
                self.process_unknown_faces(tab, containers, unknown_faces, unknown_embeddings)

    def remove_all_widget(self, layout):
        for i in reversed(range(layout.count())):
            widget_to_remove = layout.itemAt(i).widget()
            layout.removeWidget(widget_to_remove)
            widget_to_remove.setParent(None)

    def process_unknown_faces(self, tab, containers, unknown_faces, unknown_embeddings):
        first_input = None
        for face_image, embedding in zip(unknown_faces, unknown_embeddings):
            face_container = QWidget()
            face_layout = QVBoxLayout()

            face_label = QLabel()
            self.display_image(face_label, face_image, 100, 100)

            id_input = QLineEdit()
            id_input.setPlaceholderText("输入ID")
            id_input.setFixedSize(100, 30)

            if tab == "camera" and first_input is None:
                first_input = id_input

            confirm_button = QPushButton("保存")
            confirm_button.setFixedSize(100, 30)

            confirm_button.clicked.connect(
                lambda _, user_id=id_input, embedding=embedding: save_to_chroma(user_id.text(), embedding, containers,
                                                                                unknown_embeddings))

            face_layout.addWidget(face_label)
            face_layout.addWidget(id_input)
            face_layout.addWidget(confirm_button)
            face_container.setLayout(face_layout)

            containers.append(face_container)

            if tab == "entry":
                self.entry_unknown_faces_layout.addWidget(face_container)
            elif tab == "camera":
                self.camera_unknown_faces_layout.addWidget(face_container)

        if tab == "camera" and first_input:
            first_input.setFocus()

    def convert_cv_qt(self, cv_img):
        if isinstance(cv_img, np.ndarray) and cv_img is not None and cv_img.size != 0:
            rgb_image = cv2.cvtColor(cv_img, cv2.COLOR_BGR2RGB)
            h, w, ch = rgb_image.shape
            bytes_per_line = ch * w
            convert_to_Qt_format = QImage(rgb_image.data, w, h, bytes_per_line, QImage.Format_RGB888)
            return QPixmap.fromImage(convert_to_Qt_format)
        else:
            return QPixmap()

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_N:
            self.unknown_faces_requested = True

    def on_tab_change(self, index):
        if self.tabs.tabText(index) == "摄像头人脸识别":
            self.start_camera()
        else:
            self.stop_camera()

    def start_camera(self):
        self.unknown_faces_requested = False
        if not hasattr(self, 'camera_thread') or self.camera_thread is None or not self.camera_thread.isRunning():
            self.camera_thread = VideoThread()
            self.camera_thread.change_pixmap_signal.connect(self.update_images)
            self.camera_thread.fps_signal.connect(self.update_fps)
            self.camera_thread.start()

    def stop_camera(self):
        if hasattr(self, 'camera_thread') and self.camera_thread is not None and self.camera_thread.isRunning():
            self.camera_thread.stop()
            self.camera_thread = None

    def closeEvent(self, event):
        self.stop_camera()
        event.accept()

    def delete_face_info(self):
        id = self.delete_id_input.text()

        if not id:
            QMessageBox.warning(self, "警告", "请输入人脸ID")
            return

        face_collection.delete(
            ids=[id]
        )

        QMessageBox.information(self, "信息", "人脸信息删除成功")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
