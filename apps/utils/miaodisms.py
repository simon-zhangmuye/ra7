# coding=utf-8
__author__ = 'Simon Zhang'
__date__ = '2018/12/12 10:17'

import json
import requests
from datetime import datetime
import hashlib

class MiaoDiSMS(object):
    def __init__(self):
        self.account_sid = "683e6d600e9f48e7b77c2087a8dda775"
        self.auth_token = "975e57cef0144486a5de4b40d44b1508"
        self.single_send_url = "https://api.miaodiyun.com/20150822/industrySMS/sendSMS"

    def send_sms(self, code, mobile):
        timestamp = datetime.strftime(datetime.now(), "%Y%m%d%H%M%S")
        combine = self.account_sid+self.auth_token+timestamp
        sig =hashlib.md5(combine.encode(encoding="UTF-8")).hexdigest()
        parmas = {
            "accountSid": self.account_sid,
            "to": mobile,
            "smsContent": "【爱学科技】您的验证码为{code}，请于{time}分钟内正确输入，如非本人操作，请忽略此短信。".format(code=code, time=15),
            "timestamp": timestamp,
            "sig": sig

        }

        response = requests.post(self.single_send_url, data=parmas)
        print(response)
        re_dict = json.loads(response.text)
        return re_dict

# if __name__ == "__main__":
#     miaodi = MiaoDiSMS()
#     miaodi.send_sms("1111", "18001129380")


