from django.db import models


# Create your models here.

class FaceProcessingRecord(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    uploaded_image_path = models.CharField(max_length=255)
    processed_frame_path = models.CharField(max_length=255)
    key_points_image_path = models.CharField(max_length=255)

    # 已知的面部信息
    identity = models.CharField(max_length=100)
    confidence = models.FloatField()
    gender = models.CharField(max_length=10)
    age = models.IntegerField()
    embedding = models.JSONField()

    def __str__(self):
        return f"FaceProcessingRecord (ID: {self.identity}, Confidence: {self.confidence})"


class UnknownFace(models.Model):
    record = models.ForeignKey(FaceProcessingRecord, related_name="unknown_faces", on_delete=models.CASCADE)
    face_image_path = models.CharField(max_length=255)
    embedding = models.JSONField()

    def __str__(self):
        return f"UnknownFace for record {self.record.id}"
