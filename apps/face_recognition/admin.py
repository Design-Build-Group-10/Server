from django.contrib import admin

from apps.face_recognition.models import FaceProcessingRecord, UnknownFace

# Register your models here.

admin.site.register(FaceProcessingRecord)
admin.site.register(UnknownFace)
