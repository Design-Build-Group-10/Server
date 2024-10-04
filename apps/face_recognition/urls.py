from django.urls import path

from apps.face_recognition.views.chroma_client import FaceEntryView, FaceDeleteView
from apps.face_recognition.views.face_process import FaceProcessingView

app_name = 'face_recognition'

urlpatterns = [
    path('/process', FaceProcessingView.as_view(), name='人脸识别'),
    path('/entry', FaceEntryView.as_view(), name='人脸信息录入'),
    path('/delete', FaceDeleteView.as_view(), name='删除人脸信息'),
]
