# coding=utf-8
__author__ = 'Simon Zhang'
__date__ = '2018/12/16 5:40'

from django.contrib.auth import get_user_model
User = get_user_model()
from django.db.models import Q
from django.contrib.auth.backends import ModelBackend


class CustomBackend(ModelBackend):
    """
    自定义用户验证规则
    """

    def authenticate(self, request, username=None, password=None, **kwargs):
        try:
            # 不希望用户存在两个，get只能有一个。两个是get失败的一种原因
            # 后期可以添加邮箱验证
            user = User.objects.get(Q(username=username) | Q(mobile=username) | Q(email=username))
            # django的后台中密码加密：所以不能password==password
            # UserProfile继承的AbstractUser中有def check_password(self, raw_password):
            if user.check_password(password):
                return user
        except Exception as e:
            return None