"""config URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls.py import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls.py'))
"""
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('user/', include('apps.user.urls')),
    path('face/', include('apps.face_recognition.urls'), name='人脸识别系统'),
    path('robot/', include('apps.robot.urls'), name='机器人管理系统'),
    path('product/', include('apps.product.urls')),
    path('shop/', include('apps.shop.urls')),
    path('cart/', include('apps.cart.urls')),
    path('order/', include('apps.order.urls')),
]
