# coding=utf-8
__author__ = 'Simon Zhang'
__date__ = '2018/12/21 18:29'
import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "ra7.settings")
import django
django.setup()
import random
from faker import Faker
from users.models import UserProfile
faker = Faker()


def create_fake_user():
    for i in range(0,500):
        gender = random.choice(["male","female"])
        mobile = 13273646088 +i
        user =UserProfile.objects.create(username=faker.name(), gender=gender,
                                  birthday=faker.date_of_birth(), mobile=mobile,
                                  email=faker.email(), image=faker.image_url(100,100))
        user.set_password("123123")
        user.save()

def delete_user():
    records = UserProfile.objects.filter(id__gt= 11)
    records.delete()


if __name__ == '__main__':
    delete_user()