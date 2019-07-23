"""ra7 URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include, re_path
from rest_framework import routers
from users.views import UserMobileViewset,SmsForNew, SmsForExisted, UserEmailViewSet, AdminViewset, StaffViewset
from ra7.settings import MEDIA_ROOT
from django.views.static import serve
router = routers.DefaultRouter()
# 配置手机注册users的管理的url
router.register('home/users', UserMobileViewset, base_name='users_mobile')
# 配置邮箱注册users的管理的url
router.register('home/accounts', UserEmailViewSet, base_name='users_email')
#admin用户管理页面
router.register('home/admin', AdminViewset, base_name='admin')
#staff用户管理页面
router.register('home/staff', StaffViewset, base_name='admin')

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include(router.urls)),
    #用户登录
    path('auth/', include('apps.auth.urls'), name="auth"),
    path('home/', include('apps.users.urls'), name='home'),

    # 配置新用户注册发送验证码，发送验证码更换注册手机的url
    path('code/new/', SmsForNew.as_view(), name ='code_new'),
    # 配置老用户发送验证登录按修改密码的url
    path('code/existed/', SmsForExisted.as_view(), name='code_existed'),
    # 处理图片显示的url,使用Django自带serve,传入参数告诉它去哪个路径找，我们有配置好的路径MEDIAROOT
    re_path('media/(?P<path>.*)', serve, {"document_root": MEDIA_ROOT}),
]
