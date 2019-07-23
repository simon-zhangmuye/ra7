# coding=utf-8
__author__ = 'Simon Zhang'
__date__ = '2018/12/16 13:07'


from django.urls import path, include
from rest_framework_jwt.views import obtain_jwt_token
from users.views import PhoneLogin

urlpatterns = [
    # 调试登录
    path('login/', include('rest_framework.urls'), name='session_login'),
    # jwt的token认证
    path('jwt/', obtain_jwt_token, name='jwt_login'),
    # #用户手机登录
    path('phone/', PhoneLogin.as_view(), name='phone_login'),
]