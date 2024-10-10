import cv2
import numpy as np


def detect_face_in_image(bytes_data):
    # 加载人脸检测的Haar级联分类器
    face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

    # 将二进制数据转换为NumPy数组
    image_np = np.frombuffer(bytes_data, np.uint8)

    # 解码图像
    image = cv2.imdecode(image_np, cv2.IMREAD_COLOR)

    if image is None:
        return False

    # 转换为灰度图像以提高检测效率
    gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # 检测图像中的人脸
    faces = face_cascade.detectMultiScale(gray_image, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))

    print(f"Detected {len(faces)} face(s) in the image.")

    return len(faces) > 0
