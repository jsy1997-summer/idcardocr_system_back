#!/usr/bin/env python
import base64
import os
import sys
import time

import django as django
import numpy as np

from bottle import response


# from django.shortcuts import HttpResponse
from idcard_ocr.method.en_de_code import *
from idcard_ocr.method import idcard_recognize


from django.http import HttpResponse, response

# 定义全局变量，用于存放图像加密之后的数据
image_encryptdata = ""
# 第一个序列的起始位置
fir_head = 0
# 第二个序列的起始位置
sec_head = 0
# 密文的长度
cip_length = 688


# 获取数据的接口，把前端得到的加密过后的图像数据放在内存里面
def get_data(request):
    if request.method == "OPTIONS":
        response.status_code = 200
        return HttpResponse("200")
    if request.method == "POST":
        body = request.body
        body = json.loads(body)
        global image_encryptdata
        image_encryptdata = body.get('img_base64')
        global fir_head, sec_head, cip_length
        fir_head = body.get('fir_head')
        sec_head = body.get('sec_head')
        # print(body)

        return HttpResponse("200 ok!")


# 信息加密识别
def idcard_ocr(request):
    if request.method == "OPTIONS":
        response.status_code = 200
        return HttpResponse("200")
    if request.method == "POST":
        t1 = round(time.time() * 1000)
        img = miser_decode(fir_head, sec_head, image_encryptdata)  # 前端传过来的加密数据的解密过程

        t2 = round(time.time() * 1000)
        print("解密的时间是%d", (t2 - t1))
        # body = request.body
        # body = json.loads(body)
        img = img.split(",")[1]

        format_img = base64.b64decode(img)  # base64解码
        file = open('idcard_ocr/testimages/change.jpg', "wb")
        file.write(format_img)
        file.close()
        image = "idcard_ocr/testimages/change.jpg"
        idcardpro = idcard_recognize.Process()
        result = idcardpro.process(image)
        t3 = round(time.time() * 1000)
        f, s, endata = miser_encode(result)
        t4 = round(time.time() * 1000)
        print("加密的时间是%d", (t4 - t3))
        res = {
            "fir": f,
            "sec": s,
            "cip_all": endata,
        }
        # print(res)

        return HttpResponse(json.dumps(res, ensure_ascii=False), content_type="text/html,charset=utf-8")
        # return HttpResponse(res)


# 信息不加密直接识别
def card_ocr(request):
    if request.method == "OPTIONS":
        response.status_code = 200
        return HttpResponse("200")
    if request.method == "POST":
        body = request.body
        body = json.loads(body)
        img = body.get("img_base64")

        eg1 = CardRecognition()
        result = eg1.nocode_reg(img)

        return HttpResponse(json.dumps(result, ensure_ascii=False), content_type="text/html,charset=utf-8")


# 信息不加密直接识别
class CardRecognition:
    def __init__(self):
        pass

    @staticmethod
    def nocode_reg(image):
        img = image.split(",")[1]
        img = base64.b64decode(img)
        file = open('idcard_ocr/testimages/change.jpg', "wb")
        file.write(img)
        file.close()
        image = "idcard_ocr/testimages/change.jpg"
        idcardpro = idcard_recognize.Process()
        result = idcardpro.process(image)
        return result


if __name__ == "__main__":

    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "IDcard_recog.settings")
    django.setup()
    # process('idcard_ocr/testimages/1.jpg')
    try:
        from django.core.management import execute_from_command_line
    except ImportError:
        # The above import may fail for some other reason. Ensure that the
        # issue is really that Django is missing to avoid masking other
        # exceptions on Python 2.
        try:
            import django
        except ImportError:
            raise ImportError(
                "Couldn't import Django. Are you sure it's installed and "
                "available on your PYTHONPATH environment variable? Did you "
                "forget to activate a virtual environment?"
            )
        raise
    execute_from_command_line(sys.argv)
