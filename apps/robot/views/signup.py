from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework_simplejwt.authentication import JWTAuthentication

from apps.robot.models import Robot
from apps.robot.serializers import RobotSerializer
from common.utils.response import bad_request_response, success_response


class RobotRegisterView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]  # 只有登录的用户可以注册机器人

    def post(self, request):
        # 1. 验证序列化器的输入数据
        serializer = RobotSerializer(data=request.data)
        if serializer.is_valid():
            serial_number = serializer.validated_data['serial_number']

            # 2. 检查是否已经存在具有相同 serial_number 的机器人
            robot = Robot.objects.filter(serial_number=serial_number).first()

            if robot:
                # 3. 如果机器人已经存在，检查用户是否已经绑定了该机器人
                if robot in request.user.robots.all():
                    return bad_request_response("This robot is already associated with the user.")

                # 4. 将已存在的机器人与当前用户绑定
                request.user.robots.add(robot)
                return success_response({
                    "robot": RobotSerializer(robot).data
                }, message="Robot already exists, but has been successfully linked to the user.")

            # 5. 如果机器人不存在，创建机器人并保存到 Robot 表
            robot = serializer.save()

            # 6. 将机器人与当前用户绑定
            request.user.robots.add(robot)

            return success_response({
                "robot": RobotSerializer(robot).data
            }, message="Robot registered and linked to the user successfully")

        # 如果输入数据不合法，返回错误信息
        return bad_request_response(serializer.errors)
