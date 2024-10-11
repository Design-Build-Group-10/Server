from django.urls import path

from apps.robot.views.create import RobotCreateView
from apps.robot.views.profile import UserRobotInfoView
from apps.robot.views.signup import RobotRegisterView

app_name = 'robot'

urlpatterns = [
    path('create/', RobotCreateView.as_view(), name='robot-create'),
    path('signup/', RobotRegisterView.as_view(), name='robot-register'),
    path('info/', UserRobotInfoView.as_view(), name='user-robot-info'),
]
