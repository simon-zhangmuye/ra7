# coding=utf-8
__author__ = 'Simon Zhang'
__date__ = '2018/12/16 5:44'

from django.contrib.auth import get_user_model
User = get_user_model()
from django.contrib.auth.backends import ModelBackend
from users.models import MobileVerifyCode
from rest_framework import status
from rest_framework.response import Response


class PhoneBackend(ModelBackend):

    def __init__(self, *args, **kwargs):
        self.user_model = get_user_model()

    def authenticate(self, request, mobile=None, code=None, **kwargs):
        verify_records = MobileVerifyCode.objects.filter(mobile=mobile).order_by("-add_time")
        if verify_records:
            last_record = verify_records[0]
            if str(last_record) == code:
                try:
                    user = User.objects.get(mobile=mobile)
                    return user
                except Exception as e:
                    return None


