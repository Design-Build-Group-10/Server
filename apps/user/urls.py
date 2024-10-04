from django.urls import path

from apps.user.views.profile import ProfileView, UserAvatar, UserFace
from apps.user.views.signIn import LoginView, FaceLoginView
from apps.user.views.signup import RegisterView

app_name = 'user'

urlpatterns = [
    path('', ProfileView.as_view(), name='用户个人信息'),
    path('/signup', RegisterView.as_view(), name='注册'),
    path('/signIn', LoginView.as_view(), name='登录'),
    path('/face/signIn', FaceLoginView.as_view(), name='人脸登录'),
    path("/avatar", UserAvatar.as_view(), name='用户头像'),
    path('/face', UserFace.as_view(), name='绑定用户人脸信息'),
]
