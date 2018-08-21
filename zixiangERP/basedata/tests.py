from django.test import TestCase

# Create your tests here.
# -*- coding:utf-8 -*-
from django.test import TestCase

# Create your tests here.
from . import models

class UserTestCase(TestCase):
    def setUp(self):
        print("创建用户")
        models.titleInfo.objects.create()
        models.User.objects.create(password=123456,username="zhangsan",first_name="张",last_name="三")
        models.Employee_info.objects.create(name="张三",user_id=0, title_id= 0,)

