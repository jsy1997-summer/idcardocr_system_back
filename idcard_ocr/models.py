from django.db import models

# Create your models here.
from django.db import models


class UserInfo(models.Model):
    # IntegerField:整数
    # CharField:字符串，参数max_length表示最大字符个数
    name = models.CharField(max_length=20, primary_key=True)
    password = models.CharField(max_length=30)

    image = models.CharField(max_length=100, default="")


class RegistInfo(models.Model):
    idnum = models.CharField(max_length=20, primary_key=True)
    path = models.CharField(max_length=50)
