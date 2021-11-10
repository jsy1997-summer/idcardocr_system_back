import base64
import json
import os
import sys
from urllib import parse

import django
import requests
from django.http import HttpResponse, response
import manage
from idcard_ocr.models import RegistInfo

card_image = ""


class FaceContrast:
    def __init__(self):
        pass

    @staticmethod
    def get_token():
        host = 'https://aip.baidubce.com/oauth/2.0/token?grant_type=client_credentials&client_id' \
               '=h1TF6RlehCIAHLsmBP8wVMAF&client_secret=CyV22SV4jjTPxYthG21eLI7s6miej0NS'
        response1 = requests.get(host)

        res1 = response1.json()
        token = res1['access_token']
        return token

    # 得到两个图片的对比结果
    def face_comp(self, card_img, live_img):
        access_token = self.get_token()  # access_token的有效期为30天，为了避免到期再次获取，每次对比就获取一次
        request_url = "https://aip.baidubce.com/rest/2.0/face/v3/match"
        request_url = request_url + "?access_token=" + access_token
        headers = {'content-type': 'application/json'}
        params = [
            {
                "image": live_img,
                "image_type": "BASE64",
                "face_type": "LIVE",
                "quality_control": "LOW",
                "liveness_control": "LOW"
            },
            {
                "image": card_img,
                "image_type": "BASE64",
                "face_type": "CERT",
                "quality_control": "LOW",
                "liveness_control": "LOW"
            }
        ]
        response0 = requests.post(request_url, json=params, headers=headers)
        resp = response0.json()
        return resp

    # 判断是否为同一个人
    def judge(self, card_img0, live_img0):
        # 预处理身份证图片  直接读取的
        card_img0 = base64.b64encode(card_img0)  # 转换为base64格式
        card_img0 = str(card_img0)
        card_img0 = card_img0.split("'")[1]

        # 预处理抓拍照片  前端传来的
        # live_img0 = base64.b64encode(live_img0)
        # live_img0 = str(live_img0)
        live_img0 = live_img0.split(",")[1]

        result = self.face_comp(card_img0, live_img0)
        result = result['result']

        if result is None:
            # tip = "未能检测出任何结果，请摆正坐姿"
            tip = "没检测出来 >_<"
        else:
            score = result['score']
            if score >= 80:
                tip = "是同一个人"
            else:
                tip = "不是同一个人，有替考嫌疑"
        return tip

    # 本地图片调用测试
    def test(self, card_img0, live_img0):
        # 预处理身份证图片
        card_img0 = base64.b64encode(card_img0)  # 转换为base64格式
        card_img0 = str(card_img0)
        card_img0 = card_img0.split("'")[1]

        # 预处理抓拍照片
        live_img0 = base64.b64encode(live_img0)
        live_img0 = str(live_img0)
        card_img0 = card_img0.split("'")[1]

        result = self.face_comp(card_img0, live_img0)
        result = result['result']

        if result is None:
            # tip = "未能检测出任何结果，请摆正坐姿"
            tip = "没检测出来 >_<"
        else:
            score = result['score']
            if score >= 80:
                tip = "是同一个人呢"
            else:
                tip = "不是同一个人，有替考嫌疑"
        return tip


# 接收前端传来的注册信息数据
def get_image(request):
    if request.method == "OPTIONS":
        response.status_code = 200
        return HttpResponse("200")
    if request.method == "POST":
        body = request.body
        body = json.loads(body)
        cardimg = body.get('card_image')
        eg2 = manage.CardRecognition()
        result = eg2.nocode_reg(cardimg)
        idnum = result['idnum']

        cardimg = cardimg.split(',')[1]
        cardimg = base64.b64decode(cardimg)
        file = open('E:/myvue/contrast_image/' + idnum + '.jpg', "wb")
        file.write(cardimg)
        file.close()
        img_path = 'E:/myvue/contrast_image/' + idnum + '.jpg'

        # 存到数据库
        data = RegistInfo(idnum=idnum, path=img_path)
        data.save()
        return HttpResponse(200)
        # liveimg = body.get('live_image')


# 接收前端传来的登录信息
def login(request):
    if request.method == "OPTIONS":
        response.status_code = 200
        return HttpResponse("200")
    if request.method == "POST":
        body = request.body
        body = json.loads(body)
        idnum = body.get('idnum')
        person = RegistInfo.objects.get(idnum=idnum)
        path = person.path
        file = open(path, 'rb')
        global card_image
        card_image = file.read()
        file.close()
        return HttpResponse(200)


# 接收前端传来的拍照信息并返回结果
def contrast(request):
    if request.method == "OPTIONS":
        response.status_code = 200
        return HttpResponse("200")
    if request.method == "POST":
        body = request.body
        body = json.loads(body)
        liveimg = body.get('live_image')
        global card_image
        eg = FaceContrast()
        result = eg.judge(card_image, liveimg)
        return HttpResponse(result)


if __name__ == "__main__":
    # BASE_DIR = os.path.dirname(os.path.abspath(__file__))  # 定位到django根目录
    # sys.path.append(os.path.abspath(os.path.join(BASE_DIR, os.pardir)))
    # os.environ.setdefault("DJANGO_SETTINGS_MODULE", "IDcard_recog.settings")  # django的settings文件
    # django.setup()

    one = FaceContrast()
    # with open('E:/myvue/contrast_image/card.txt', 'r') as f:
    #     card_image = f.read()
    # with open('E:/myvue/contrast_image/live.txt', 'r') as f:
    #     live_image = f.read()

    with open('E:/myvue/contrast_image/142822197603200075.jpg.jpg', 'rb') as f:
        card_image = f.read()
    with open('E:/myvue/contrast_image/white_jsy.jpg', 'rb') as f:
        live_image = f.read()

    res = one.test(card_image, live_image)
    print(res)
