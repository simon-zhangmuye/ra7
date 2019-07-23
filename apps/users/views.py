from django.shortcuts import render
from .serializers import UserMobileRegSerializer, UserDetailSerializer, \
    SmsForNewSerializer, SmsForExistedSerializer, PhoneLoginSerializer, ChangePhoneNumberSerializer, \
    ChangePasswordByPhoneSerializer, UserEmailRegSerializer, EmailForgetPasswordSerializer, \
    EmailUpdateEmailSerializer
from .admin_serializer import AdminSerializer, AdminCreatePutSerializer, StaffSerializer
from rest_framework import mixins, permissions, authentication, viewsets, status
from random import choice
from utils.miaodisms import MiaoDiSMS
from .models import MobileVerifyCode, EmailVerifyRecord
from rest_framework.response import Response
from django.contrib.auth import get_user_model
User = get_user_model()
from rest_framework_jwt.authentication import JSONWebTokenAuthentication
from rest_framework_jwt.serializers import jwt_payload_handler, jwt_encode_handler
from django.contrib.auth import authenticate, login
from rest_framework.generics import CreateAPIView
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet
from django.contrib.auth import update_session_auth_hash
from datetime import datetime, timedelta
from apps.utils.send_email import send_email
# Create your views here.

class SmsForNew(CreateAPIView):
    """
    给未注册用户发送验证码，修改注册手机
    method: create 发送注册码到手机用户
    status:"0"为失败，“1”为成功,
    """
    serializer_class = SmsForNewSerializer

    def generate_code(self):
        """
        生成四位数字的验证码字符串
        """
        seeds = "1234567890"
        random_str = []
        for i in range(4):
            random_str.append(choice(seeds))
        return "".join(random_str)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        mobile = serializer.validated_data["mobile"]
        miao_di = MiaoDiSMS()
        code = self.generate_code()
        sms_status = miao_di.send_sms(code=code, mobile=mobile)

        if sms_status["respCode"] == "00000":
            code_record = MobileVerifyCode(code=code, mobile=mobile)
            code_record.save()
            return Response({
                "status": "1",
                "mobile": mobile
            }, status=status.HTTP_201_CREATED)
        else:
            return Response({
                "status": "0",
                "mobile": sms_status["respDesc"]
            }, status=status.HTTP_400_BAD_REQUEST)


class SmsForExisted(SmsForNew):
    """
    给已经注册的用户发送短信验证码修改密码
    """
    serializer_class = SmsForExistedSerializer


class UserMobileViewset(mixins.CreateModelMixin, mixins.UpdateModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    """
    用户
    """
    serializer_class = []
    queryset = User.objects.all()
    authentication_classes = [JSONWebTokenAuthentication, authentication.SessionAuthentication]
    permission_classes = []

    def get_serializer_class(self):
        if self.action == "create":
            return UserMobileRegSerializer
        return UserDetailSerializer

    # permission_classes = (permissions.IsAuthenticated, )
    def get_permissions(self):
        if self.action == "retrieve":
            return [permissions.IsAuthenticated()]
        elif self.action == "create":
            return []
        return []

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = self.perform_create(serializer)
        login(request, user, backend="apps.backend.custom_backend.CustomBackend")
        re_dict = {
            "id": user.id,
            "username": user.username,
            "status": "1",
            "msg": "欢迎注册xxxx!! -- 系统自动消息"
        }
        payload = jwt_payload_handler(user)
        re_dict["token"] = jwt_encode_handler(payload)

        return Response(re_dict, status=status.HTTP_201_CREATED)

    # 重写该方法，不管传什么id，都只返回当前用户
    def get_object(self):
        return self.request.user

    def perform_create(self, serializer):
        return serializer.save()


class UserEmailViewSet(UserMobileViewset):
    def get_serializer_class(self):
        if self.action == "create":
            return UserEmailRegSerializer
        return UserDetailSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = self.perform_create(serializer)
        send_email(user.email, "register")
        re_dict = {
            "id": user.id,
            "username": user.username,
            "status": "1",
            "msg": "欢迎注册xxxx!! -- 系统自动消息"
        }
        return Response(re_dict, status=status.HTTP_201_CREATED)


class PhoneLogin(CreateAPIView):
    """
    手机登录，生成token并返回前端
    """
    queryset = User.objects.all()
    serializer_class = PhoneLoginSerializer
    authentication_classes = []
    permission_classes = []

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        mobile = request.data.get("mobile")
        code = request.data.get("code")
        try:
            user = authenticate(request, mobile=mobile, code=code, **kwargs)
            login(request, user, backend="apps.backend.phone_backend")
            re_dict ={
                "id": user.id,
                "username": user.username,
                "last_login": user.last_login,
                "status": "1",
                "msg": "手机登录成功"
            }
            payload = jwt_payload_handler(user)
            re_dict["token"] = jwt_encode_handler(payload)
            return Response(re_dict, status=status.HTTP_202_ACCEPTED)

        except Exception as e:
            re_dict = {
                "status": "0",
                "msg": "登录失败，请输入正确的验证码和手机号"
            }
            return Response(re_dict, status=status.HTTP_400_BAD_REQUEST)


class ChangePhone(CreateAPIView):
    """
    修改手机号码
    post :手机验证码
    """
    queryset = User.objects.all()
    serializer_class = ChangePhoneNumberSerializer
    authentication_classes = [JSONWebTokenAuthentication, authentication.SessionAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        code = request.data.get("code")

        verify_records = MobileVerifyCode.objects.filter(code=code).order_by("-add_time")
        if verify_records:
            # 获取到最新一条
            last_record = verify_records[0]
            mobile = last_record.mobile
            user = request.user
            user.mobile = mobile
            user.save()
            re_dict = {
                "id": user.id,
                "username": user.username,
                "mobile": user.mobile,
                "status": "1",
                "msg": "修改手机号码成功"
            }
            return Response(re_dict, status=status.HTTP_201_CREATED)
        else:
            re_dict = {
                "status": "0",
                "msg": "请输入正确的验证码"
            }
            return Response(re_dict, status=status.HTTP_400_BAD_REQUEST)


class ChangePasswordByPhone(CreateAPIView):
    serializer_class = ChangePasswordByPhoneSerializer
    authentication_classes = [JSONWebTokenAuthentication, authentication.SessionAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        code = request.data.get("code")
        password = request.data.get("password")
        verify_records = MobileVerifyCode.objects.filter(code=code).order_by("-add_time")
        if verify_records:
            user = request.user
            user.set_password(password)
            user.save()
            re_dict = {
                "id": user.id,
                "username": user.username,
                "status": "1",
                "msg": "修改密码成功!! -- 系统自动消息"
            }
            payload = jwt_payload_handler(user)
            re_dict["token"] = jwt_encode_handler(payload)
            update_session_auth_hash(request,user)
            return Response(re_dict, status=status.HTTP_201_CREATED)
        else:
            re_dict = {
                "status": "0",
                "msg": "请输入正确的验证码"
            }
            return Response(re_dict, status=status.HTTP_400_BAD_REQUEST)


class EmailActive(APIView):
    def get(self, request, code):
        if code:
            record = EmailVerifyRecord.objects.filter(code=code, send_type="register").order_by("-send_time").first()
            # 有效期为两小时。
            two_hours_ago = datetime.now() - timedelta(hours=23, minutes=0, seconds=0)
            if not record:
                re_dict = {
                    "status": "0",
                    "msg": "非可用验证码，操作失败"
                }
                return Response(re_dict, status=status.HTTP_406_NOT_ACCEPTABLE)
            if two_hours_ago > record.send_time:
                re_dict = {
                    "status": "0",
                    "msg": "验证码超过两小时，请从新发送验证码"
                }
                return Response(re_dict, status=status.HTTP_406_NOT_ACCEPTABLE)
            user = User.objects.get(email=record.email)
            user.is_active = True
            user.save()
            login(request, user, backend="apps.backend.custom_backend.CustomBackend")
            re_dict = {
                "username": user.username,
                "status": "1",
                "msg": "用户激活成功"
            }
            payload = jwt_payload_handler(user)
            re_dict["token"] = jwt_encode_handler(payload)
            update_session_auth_hash(request, user)
            return Response(re_dict, status.HTTP_201_CREATED)
        else:
            re_dict = {
                "status": "0",
                "msg": "非可用验证码，操作失败"
            }
            return Response(re_dict, status=status.HTTP_400_BAD_REQUEST)


class EmailForgetPassword(CreateAPIView):
    serializer_class = EmailForgetPasswordSerializer
    authentication_classes = [JSONWebTokenAuthentication, authentication.SessionAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, code):
        if code:
            record = EmailVerifyRecord.objects.filter(code=code, send_type="forget").order_by("-send_time").first()
            if not record:
                re_dict ={
                    "status": "0",
                    "msg": "验证码错误"
                }
                return Response(re_dict, status.HTTP_403_FORBIDDEN)
            # 有效期为两小时。
            two_hours_ago = datetime.now() - timedelta(hours=22, minutes=0, seconds=0)
            if two_hours_ago > record.send_time:
                re_dict ={
                    "status": "0",
                    "msg": "验证码错误"
                }
                return Response(re_dict, status.HTTP_403_FORBIDDEN)
            re_dict = {
                "status": "1",
                "msg": "验证通过，请输入用户的新密码"
            }
            return Response(re_dict, status.HTTP_202_ACCEPTED)

        else:
            re_dict = {
                "status": "0",
                "msg": "验证码错误"
            }
            return Response(re_dict, status.HTTP_403_FORBIDDEN)

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = request.user
        password = request.data.get("password")
        user.set_password(password)
        user.save()
        re_dict = {
            "id": user.id,
            "username": user.username,
            "status": "1",
            "msg": "修改密码成功!! -- 系统自动消息"
        }
        payload = jwt_payload_handler(user)
        re_dict["token"] = jwt_encode_handler(payload)
        update_session_auth_hash(request, user)
        return Response(re_dict, status=status.HTTP_201_CREATED)


class SendEmailForgetPassword(APIView):
    authentication_classes = [JSONWebTokenAuthentication, authentication.SessionAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        user = request.user
        email = user.email
        send_email(email, "forget")
        re_dict = {
            "status": "1",
            "msg": "已发送到用户邮箱，请点击里边的链接修改密码"
        }
        return Response(re_dict, status.HTTP_201_CREATED)


class SendEmailUpdateEmail(CreateAPIView):
    serializer_class = EmailUpdateEmailSerializer
    authentication_classes = [JSONWebTokenAuthentication, authentication.SessionAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = request.data.get("email")
        send_email(email, "update")
        user = request.user
        record = EmailVerifyRecord.objects.filter(email=email).order_by("-send_time").first()
        record.user_email = user.email
        record.save()
        re_dict = {
            "status": "1",
            "msg": "已发送到{email}邮箱，请点击里边的链接修改密码,如果收件箱查收不到请检查垃圾邮件。".format(email=email)
        }
        return Response(re_dict, status.HTTP_201_CREATED)


class EmailUpdate(APIView):
    def get(self, request, code):
        if code:
            record = EmailVerifyRecord.objects.filter(code=code, send_type="update").order_by("-send_time").first()
            # 有效期为两小时。
            two_hours_ago = datetime.now() - timedelta(hours=23, minutes=0, seconds=0)
            if not record:
                re_dict = {
                    "status": "0",
                    "msg": "非可用验证码，操作失败"
                }
                return Response(re_dict, status=status.HTTP_406_NOT_ACCEPTABLE)
            if two_hours_ago > record.send_time:
                re_dict = {
                    "status": "0",
                    "msg": "验证码超过两小时，请从新发送验证码"
                }
                return Response(re_dict, status=status.HTTP_406_NOT_ACCEPTABLE)
            user = User.objects.get(email=record.user_email)
            user.email = record.email
            user.save()
            login(request, user, backend="apps.backend.custom_backend.CustomBackend")
            re_dict = {
                "username": user.username,
                "status": "1",
                "msg": "用户更新邮件成功"
            }
            payload = jwt_payload_handler(user)
            re_dict["token"] = jwt_encode_handler(payload)
            update_session_auth_hash(request, user)
            return Response(re_dict, status.HTTP_201_CREATED)
        else:
            re_dict = {
                "status": "0",
                "msg": "非可用验证码，操作失败"
            }
            return Response(re_dict, status=status.HTTP_400_BAD_REQUEST)


class AdminViewset(ModelViewSet):
    serializer_class = []
    queryset = User.objects.all()
    authentication_classes = [JSONWebTokenAuthentication, authentication.SessionAuthentication]
    permission_classes = [permissions.IsAdminUser]

    def get_serializer_class(self):
        if self.action == "update" or self.action == "create":
            return AdminCreatePutSerializer
        return AdminSerializer


class StaffViewset(mixins.UpdateModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    serializer_class = StaffSerializer
    queryset = User.objects.filter(is_superuser=False)
    authentication_classes = [JSONWebTokenAuthentication, authentication.SessionAuthentication]
    permission_classes = [permissions.IsStaffUser]
    lookup_field = 'mobile'
