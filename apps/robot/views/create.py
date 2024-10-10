from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework_simplejwt.authentication import JWTAuthentication

from apps.robot.models import Robot
from apps.robot.serializers import RobotSerializer
from common.utils.response import success_response, bad_request_response


# 暂时弃用
class RobotCreateView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]  # 只有登录的用户可以添加机器人

    def post(self, request):
        # 1. 验证请求中的机器人数据
        serializer = RobotSerializer(data=request.data)
        if serializer.is_valid():
            serial_number = serializer.validated_data['serial_number']

            # 2. 检查是否已经存在具有相同 serial_number 的机器人
            if Robot.objects.filter(serial_number=serial_number).exists():
                return bad_request_response("Robot with this serial number already exists.")

            # 3. 将机器人信息录入 Robot 表
            robot = serializer.save()

            return success_response({
                "robot": RobotSerializer(robot).data
            }, message="Robot added successfully")

        # 如果数据无效，返回错误信息
        return bad_request_response(serializer.errors)
