import base64
import json
import time

from django.shortcuts import render

# Create your views here.

from idcard_ocr.models import UserInfo
from django.http import HttpResponse, response
from django.http import JsonResponse


# 用户注册
def register(request):
    if request.method == "OPTIONS":
        response.status_code = 200
        return HttpResponse("200")  # 跨域请求会有一次OPTION请求，手动返回一个200状态码，才会再次发送post请求
    if request.method == "POST":
        body = request.body
        body = json.loads(body)
        # postBody = eval(str(request.body, encoding='utf-8'))
        username = body.get('user_name')
        upassword = body.get('user_password')
        image = body.get('user_image')
        image = image.split(",")[1]
        format_img = base64.b64decode(image)  # base64解码
        file = open('E:/myvue/my_idcard_system/idcardocr_system_front/src/assets/'+username+'.jpg', "wb")
        file.write(format_img)
        file.close()
        # with open('E:/myvue/my_idcard_system/idcardocr_system_front/src/assets/'+username+'.jpg', "rb") as f:
        #     img = f.read()
        #
        # image = base64.b64encode(img)
        # print(image)
        image_url = 'E:/myvue/my_idcard_system/idcardocr_system_front/src/assets/'+username+'.jpg'  # 头像存储的是在前端的额相对路径

        data = UserInfo(name=username, password=upassword, image=image_url)  # 填写多个字段的数据
        data.save()  # 完成操作
        return HttpResponse("200")


# 用户登录
def login(request):
    if request.method == "OPTIONS":
        response.status_code = 200
        return HttpResponse("200")
    if request.method == "POST":
        body = request.body
        body = json.loads(body)
        username = body.get('user_name')
        person = UserInfo.objects.get(name=username)
        password = person.password
        # image_url = person.image
        # res = {
        #     "password": password,
        #     "url": image_url,
        # }
        # return HttpResponse(json.dumps(res, ensure_ascii=False), content_type="text/html,charset=utf-8")
        return HttpResponse(password)


#  用户修改密码
def updata(request):
    if request.method == "OPTIONS":
        response.status_code = 200
        return HttpResponse("200")
    if request.method == "POST":
        body = request.body
        body = json.loads(body)
        username = body.get('user_name')
        oldpassword = body.get('oldpassword')
        newpassword = body.get('newpassword')
        person = UserInfo.objects.get(name=username)
        password = person.password
        if password == oldpassword:
            person.password = newpassword
            person.save()
            return HttpResponse("已经修改")
        else:
            return HttpResponse("您的密码不正确")


#  用户忘记密码
def forget(request):
    if request.method == "OPTIONS":
        response.status_code = 200
        return HttpResponse("200")
    if request.method == "POST":
        body = request.body
        body = json.loads(body)
        username = body.get('user_name')
        newpassword = body.get('newpassword')
        person = UserInfo.objects.get(name=username)
        person.password = newpassword
        person.save()
        return HttpResponse("已经修改")


# 身份证信息导出为txt格式文件
def idcardInfoExport(request):
    if request.method == "OPTIONS":
        response.status_code = 200
        return HttpResponse("200")
    if request.method == "POST":
        body = request.body
        body = json.loads(body)
        info = body.get('download_info')  # dict格式
        print(info)
        info = str(info)  # 转换为str格式
        print(info)
        time_stamp = str(time.time())
        export_path = "D:/" + "身份证信息表 " + time_stamp + '.txt'
        file = open(export_path, mode='w')
        file.write(info)
        return HttpResponse(export_path)
