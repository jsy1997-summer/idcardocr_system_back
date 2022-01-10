import base64
import random

import django
import json
import os
import sys

import numpy as np
import requests
from django.http import HttpResponse, response

import manage

# 因为本文件和views以及model不在同级目录
# sys.path.append('../')
# 根据报错信息进行配置，调用Django的环境变量
# os.environ.setdefault("DJANGO_SETTINGS_MODULE", "IDcard_recog.settings")
# django.setup()

from idcard_ocr.models import RegistInfo

card_image = ""
# 存储左右扭头的数据集
yaw_result = []
# 存储低头次数的数据集
pitch_result = []
# 存储人脸完整度的数据集
completeness_result = []
# 存储每次左右眼之间的距离
eye_gap = []
# 存储每次嘴巴和鼻子之间的距离
nm_gap = []


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

    # 活体检测，避免用照片或者脸模
    def living_detect(self, image):
        image = image.split(",")[1]
        # access_token = self.get_token()
        # request_url = "https://aip.baidubce.com/rest/2.0/face/v3/faceverify"
        # request_url = request_url + "?access_token=" + access_token
        # headers = {'content-type': 'application/json'}
        # params = [
        #     {
        #         "image": image,
        #         "image_type": "BASE64",
        #         "face_field": "expression,landmark,quality",
        #         "option": "COMMON"
        #
        #     },
        # ]  # expression(表情),landmark（特征点位置）
        # response0 = requests.post(request_url, json=params, headers=headers)
        # resp = response0.json()
        # print(resp)
        # 人脸信息列表
        # result = resp['result']
        # face_liveness = result['face_liveness']
        # tip = ""
        # # 活体检测验证，避免考生使用照片或者视频通过人脸检测,阈值为0.3的置信概率为99.9%
        # if face_liveness < 0.3:
        #     tip = tip + "有用照片或者视频通过人脸验证作弊的嫌疑"
        # face_list = result['face_list'][0]
        # yaw = face_list['angle']['yaw']
        # pitch = face_list['angle']['pitch']
        # # print("左右旋转角度：" + str(yaw))
        # # print("上下旋转角度：" + str(pitch))
        # #  判断是否长时间左右扭头，左右扭动20deg，判断为左右扭头
        # if abs(yaw) > 20:
        #     yaw_result.append(1)
        # else:
        #     yaw_result.append(0)
        # yaw_percent = self.percent(yaw_result)
        # yaw_sum = [0.1, 0.25, 0.5, 0.75]
        # yaw_tip = ['行为正常', '时常左顾右盼，有作弊嫌疑', '经常左顾右盼，有作弊嫌疑', '半数时间以上左顾右盼', "长时间左顾右盼，可判为作弊"]
        # tip = tip + "；" + self.action_judge(yaw_percent, yaw_sum, yaw_tip)
        #
        # # 判断是否长时间低头，大于30deg，判断为低头
        # if abs(pitch) > 30:
        #     pitch_result.append(1)
        # else:
        #     pitch_result.append(0)
        # pitch_percent = self.percent(pitch_result)
        # pitch_sum = [0.1, 0.25, 0.5, 0.75]
        # pitch_tip = ['行为正常', '时常低头，有作弊嫌疑', '经常低头，有作弊嫌疑', '半数时间以上低头', "长时间低头，可判为作弊"]
        # tip = tip + "；" + self.action_judge(pitch_percent, pitch_sum, pitch_tip)
        #
        # # 判断脸部是否长时间被遮挡
        # completeness = face_list['quality']['completeness']
        # if completeness < 0.5:
        #     completeness_result.append(1)
        # else:
        #     completeness_result.append(0)
        # completeness_percent = self.percent(completeness_result)
        # completeness_sum = [0.1, 0.25, 0.5, 0.75]
        # completeness_tip = ['行为正常', '时常脸部被遮挡，有作弊嫌疑', '经常脸部被遮挡，有作弊嫌疑', '半数时间以上脸部被遮挡', "长时间脸部被遮挡，可判为作弊"]
        # tip = tip + "；" + self.action_judge(completeness_percent, completeness_sum, completeness_tip)
        #
        # # 脸部特征点之间的距离变化，防止3d打印脸模型
        # # 两眼之间的距离
        # ey = np.array([face_list["landmark"][0]['x'], face_list["landmark"][0]['y']])
        # ye = np.array([face_list["landmark"][1]['x'], face_list["landmark"][1]['y']])
        # eye = np.linalg.norm(ey - ye)
        # eye_gap.append(eye)
        # eye_var = np.var(eye_gap)
        # # 鼻子和嘴巴之间的距离
        # nose = np.array([face_list["landmark"][2]['x'], face_list["landmark"][2]['y']])
        # mouth = np.array([face_list["landmark"][3]['x'], face_list["landmark"][3]['y']])
        # nm = np.linalg.norm(nose - mouth)
        # nm_gap.append(nm)
        # nm_var = np.var(nm_gap)
        # # 用静态人脸测试，方差基本上都在1以下，动态人脸在1以上
        # if eye_var > 1 and nm_var > 1:
        #     tip = tip + "；" + "行为正常"
        # else:
        #     tip = tip + "；" + "有用假脸通过考试的嫌疑"
        #
        # result = {
        #     "活体率": face_liveness,
        #     "左右扭头概率": yaw_percent,
        #     "低头概率": pitch_percent,
        #     "脸部长时间被遮挡概率": completeness_percent,
        #     "左右特征点方差": eye_var,
        #     "上下特征点方差": nm_var,
        # }
        result = {
            "活体率": random.randint(0, 10) / 10,
            "左右扭头概率": random.randint(0, 10) / 10,
            "低头概率": random.randint(0, 10) / 10,
            "脸部长时间被遮挡概率": random.randint(0, 10) / 10,
            "左右特征点方差": random.randint(0, 200),
            "上下特征点方差": random.randint(0, 200),
            "result": "",
        }
        print(result)
        print("d")
        tip = 'haodedefwaf'

        return tip, result

    # 判断一个数组里面1的占比
    @staticmethod
    def percent(arr):
        length = len(arr)
        count = arr.count(1)
        return count / length

    # 根据分数值判断作弊嫌疑  p:当前分数值， percent：分数区间 tip：返回的内容列表
    @staticmethod
    def action_judge(p, percent, tip):
        if p <= percent[0]:
            return tip[0]
        elif percent[0] < p <= percent[1]:
            return tip[1]
        elif percent[1] < p <= percent[2]:
            return tip[2]
        elif percent[2] < p <= percent[3]:
            return tip[3]
        else:
            return tip[4]


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


# 接收前端传来的登录信息（是照片对比时的登录信息）
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
        # 判断是不是同一个人
        percent = {}
        # result = eg.judge(card_image, liveimg)
        result = "是同一个人"
        if result == "是同一个人":
            result1, percent = eg.living_detect(liveimg)
        else:
            result1 = ""
        result = result + result1
        percent["result"] = result

        # 判断是不是用的图片或者脸模
        return HttpResponse(json.dumps(percent, ensure_ascii=False), content_type="text/html,charset=utf-8")


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

    with open('E:/myvue/contrast_image/xz1.jpeg', 'rb') as f:
        live_image0 = f.read()
    with open('E:/myvue/contrast_image/xz.jpeg', 'rb') as f:
        live_image = f.read()
    card_img = base64.b64encode(live_image)  # 转换为base64格式
    card_img = str(card_img)
    # card_img = card_img.split("'")[1]
    res = one.living_detect(card_img)
    print(res)
