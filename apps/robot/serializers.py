from rest_framework import serializers

from apps.robot.models import Robot


class RobotSerializer(serializers.ModelSerializer):
    class Meta:
        model = Robot
        fields = ['id', 'name', 'serial_number', 'created_at', 'updated_at']

    def create(self, validated_data):
        # 创建机器人
        robot = Robot.objects.create(**validated_data)
        return robot
