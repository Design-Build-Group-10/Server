# Create your models here.
from django.db import models


class Robot(models.Model):
    """
    Robot 模型存储每个机器人的基本信息。
    """
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255)
    serial_number = models.CharField(max_length=255, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name
