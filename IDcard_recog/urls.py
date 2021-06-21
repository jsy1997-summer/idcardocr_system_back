"""IDcard_recog URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url
from django.contrib import admin
from django.urls import re_path, path

import manage
from idcard_ocr import views
from idcard_ocr.method import en_de_code

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    # url('ocr/', manage.idcard_ocr),
    re_path(r'^ocr/(\S+)', manage.idcard_ocr),  # get方式，适合传递url
    re_path(r'^ocr/$', manage.idcard_ocr),  # post方式，适合base64
    path('register/', views.register),  # 注册的访问接口
    path('login/', views.login),  # 登录验证的访问接口
    path('updata/', views.updata),  # 修改密码的访问接口
    path('forget/', views.forget),  # 忘记密码的访问接口
    path('download/', views.idcardInfoExport),  # 下载txt文件的访问接口
    path('getkey/', en_de_code.get_key),  # 获取公钥的接口
    path('senddata/', manage.get_data),  # 后端得到前端发送过来的加密之后的数据并且保存在内存中

]
