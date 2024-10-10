from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework_simplejwt.authentication import JWTAuthentication

from apps.robot.serializers import RobotSerializer
from common.utils.response import success_response  # 假设这些是你项目中的辅助函数


class UserRobotInfoView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]  # 只有登录的用户可以访问该接口

    def get(self, request):
        # 获取当前用户
        user = request.user

        # 获取当前用户关联的所有机器人
        robots = user.robots.all()

        # 如果用户没有关联机器人，返回空列表
        if not robots.exists():
            return success_response(data={"robotList": []}, message="No robots associated with this user.")

        # 序列化机器人信息
        serialized_robots = RobotSerializer(robots, many=True).data

        # 返回序列化后的机器人信息
        return success_response(data={"robotList": serialized_robots},
                                message="Robot information retrieved successfully.")
