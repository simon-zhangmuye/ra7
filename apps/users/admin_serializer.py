# coding=utf-8
__author__ = 'Simon Zhang'
__date__ = '2018/12/20 23:00'

from rest_framework.serializers import ModelSerializer
from django.contrib.auth import get_user_model
User = get_user_model()
from django.contrib.auth.models import Group, Permission


class GroupSerializer(ModelSerializer):
    class Meta:
        model = Group
        fields = ("id", "name")


class PermissionSerializer(ModelSerializer):
    class Meta:
        model = Permission
        fields = ("id", "name")


class AdminSerializer(ModelSerializer):
    groups = GroupSerializer(many=True)
    user_permissions = PermissionSerializer(many=True)

    class Meta:
        model = User
        fields = "__all__"


class AdminCreatePutSerializer(ModelSerializer):
    class Meta:
        model = User
        fields = "__all__"


class StaffSerializer(ModelSerializer):
    class Meta:
        model = User
        fields = ("id", "last_login", "username", "date_joined",
                  "gender", "birthday", "image", "mobile", "email",
                 )