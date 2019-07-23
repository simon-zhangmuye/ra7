# coding=utf-8
__author__ = 'Simon Zhang'
__date__ = '2018/12/16 15:45'


from django.urls import path, re_path
from users.views import ChangePhone, ChangePasswordByPhone, EmailActive, EmailForgetPassword, \
    SendEmailForgetPassword, SendEmailUpdateEmail, EmailUpdate

urlpatterns = [
    #用户修改手机号码
    path('change_phone/', ChangePhone.as_view(), name="change_phone"),
    path('change_password_byphone/', ChangePasswordByPhone.as_view(), name="change_password_phone"),
    path('send_email_forget_password/', SendEmailForgetPassword.as_view(), name="send_email_forget_password"),
    path('send_email_update_email/', SendEmailUpdateEmail.as_view(), name="send_email_update_email"),
    re_path('email_active/(?P<code>.*)/', EmailActive.as_view(), name='email_active'),
    re_path('email_forget/(?P<code>.*)/', EmailForgetPassword.as_view(), name='email_forget'),
    re_path('email_update/(?P<code>.*)/', EmailUpdate.as_view(), name='email_update'),
]