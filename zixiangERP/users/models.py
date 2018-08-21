# _*_encoding:utf-8 _*_
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.validators import MaxValueValidator, MinValueValidator
from common import const
from django.utils.timezone import now



class Employee(AbstractUser):

    RANK =  ((0, u"普通员工"),
             (1, u"总经理"),
             (2, u"商务经理"),
             (3, u"财务经理"),
             (4, u"工程经理"),
             (5, u"技术经理"),
             (6, u"库管"),
             (7, u"营销经理"),
             (8, u"行政经理")
             )

    nickname = models.CharField(max_length=20,default="",verbose_name=u"昵称",blank=True, null=True)
    title = models.IntegerField(verbose_name=u"权限", default=0, choices=RANK, blank=True, null=True)
    email = models.EmailField(verbose_name=u"电子邮箱",blank=True, null=True)
    phone = models.CharField(max_length=11, verbose_name=u"电话", blank=True, null=True)

    class Meta:
        verbose_name=u"职员信息"
        verbose_name_plural=u"职员信息"

    def __str__(self):
        return self.username

class EmailVerifyRecord(models.Model):
    code = models.CharField(max_length=20, verbose_name=u"验证码")
    email = models.EmailField(max_length=50, verbose_name = u"邮箱")
    sen_type = models.CharField(max_length=20,choices=(("register",u"注册"),("forget",u"忘记密码")))
    send_time = models.DateField(auto_now=True)

    class Meta:
        verbose_name = u"邮箱验证码"
        verbose_name_plural = verbose_name

