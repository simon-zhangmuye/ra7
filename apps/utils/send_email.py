# coding=utf-8
__author__ = 'Simon Zhang'
__date__ = '2018/12/14 13:29'

import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "ra7.settings")

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()

import random
from users.models import EmailVerifyRecord
# 发送html格式的邮件:
from django.template import loader
# 导入setting中发送邮件的配置
from ra7.settings import EMAIL_FROM
# 导入Django自带的邮件模块
from django.core.mail import send_mail, EmailMessage

web_url ="http://127.0.0.1:8000"

def random_str(random_length=8):
    str = ''
    #生成字符串的字段
    chars = 'AaBbCcDdEeFfGgHhIiJjKkLlMmNnOoPpQqRrSsTtUuVvWwXxYyZz0123456789'
    length = len(chars) - 1
    for i in range(random_length):
        str += chars[random.randint(0, length)]
    return str


#发送邮件
def send_email(email, send_type=None):
    # 发送之前先保存到数据库，到时候查询链接是否存在
    # 实例化一个EmailVerifyRecord对象
    email_record = EmailVerifyRecord()
    code = random_str(16)
    email_record.code = code
    email_record.email = email
    email_record.send_type = send_type
    email_record.save()

    if send_type == "register":
        email_title = "注册激活链接"
        email_body = "请点击下面的链接激活你的账号: {web_url}/home/email_active/{code}/".format(web_url=web_url, code=code)
    if send_type == "forget":
        email_title = "忘记密码链接"
        email_body = "请点击下面的链接更改你的密码: {web_url}/home/email_forget/{code}/".format(web_url=web_url, code=code)
    if send_type == "update":
        email_title = "更新邮箱链接"
        email_body = "请点击下面的链接更新你的邮箱: {web_url}/home/email_update/{code}/".format(web_url=web_url, code=code)
    send_status = send_mail(email_title, email_body, EMAIL_FROM, [email])
    return send_status



