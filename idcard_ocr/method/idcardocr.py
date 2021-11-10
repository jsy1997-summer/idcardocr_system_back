# -*- coding: utf-8 -*-
from PIL import Image
# import pytesseract
import cv2
import numpy as np
import re
# from multiprocessing import Pool, Queue, Lock, Process, freeze_support
# import time
# import matplotlib.pyplot as plt
import matplotlib.image as imashow

from idcard_ocr.method import idcard_recognize, findidcard, secverify

from pyocr.libtesseract import tesseract_raw

# pytesseract.pytesseract.tesseract_cmd = 'C:\\Program Files (x86)\\Tesseract-OCR\\tesseract.exe'
x = 1280.00 / 3840.00
pixel_x = int(x * 3840)


# print(x, pixel_x)


# mode0:识别姓名，出生日期，身份证号； mode1：识别所有信息
# s和d是为了训练参数用到的，实际不需要
def idcardocr(imgname, handle0, handle_num0, mode=1):
    print(u'进入身份证光学识别流程...')
    if mode == 1:
        # t1 = round(time.time() * 1000)
        # showing(imgname,"name")
        img_data_gray, img_org = img_resize_gray(imgname)  # img_data_gray身份证灰度图像，img_org身份证彩色图像
        result_dict = dict()

        name_pic = find_name(img_data_gray, img_org)  # name_pic得到名字图片

        # t3 = round(time.time() * 1000)
        result_dict['name'] = get_name(name_pic, handle0)
        # t4 = round(time.time() * 1000)
        # print(u'名字2耗时:%s' % (t4 - t3))

        idnum_pic = find_idnum(img_data_gray, img_org)
        new_id, new_birth = get_idnum_and_birth(idnum_pic, handle_num0)

        result_dict['sex'] = new_get_sex(new_id)
        result_dict['idnum'] = new_id
        print('idnum')
        print(new_id)
        result_dict['birth'] = new_birth
        print('birth')
        print(new_birth)

        nation_pic = find_nation(img_data_gray, img_org)
        # t5 = round(time.time() * 1000)
        result_dict['nation'] = get_nation(nation_pic, handle0)
        # t6 = round(time.time() * 1000)
        # print(u'nation2耗时:%s' % (t6 - t5))

        address_pic, firline_pic = find_address(img_data_gray, img_org)
        # t7 = round(time.time() * 1000)

        result_dict['address'] = get_address(address_pic, handle0)
        firline_text = get_address(firline_pic, handle0)
        secverify.firline_text = firline_text

    elif mode == 0:
        # generate_mask(x)
        img_data_gray, img_org = img_resize_gray(imgname)
        result_dict = dict()
        name_pic = find_name(img_data_gray, img_org)
        # showimg(name_pic)
        # print 'name'
        result_dict['name'] = get_name(name_pic)
        # print result_dict['name']

        idnum_pic = find_idnum(img_data_gray, img_org)
        # showimg(idnum_pic)
        # print 'idnum'

        result_dict['idnum'], result_dict['birth'] = get_idnum_and_birth(idnum_pic)
        result_dict['sex'] = ''
        result_dict['nation'] = ''
        result_dict['address'] = ''

    else:
        print(u"模式选择错误！")

    # showimg(img_data_gray)
    return result_dict


# 身份证真伪验证中的垂直验证
class Verify:
    def __init__(self):
        pass

    @staticmethod
    def vertical_verify(img):
        img_gray, img_org = img_resize_gray(img)
        # 获取人脸最左边的位置
        # 地址两个字的模板
        # cv2.namedWindow("tu", 0)
        # cv2.imshow("tu", img_gray)
        template = cv2.UMat(cv2.imread(r'E:/myvue/IDcard_recog/idcardocr_system_back/idcard_ocr/mask_img'
                                       r'/address_mask_%s.jpg' % pixel_x, 0))
        # 地址模板两个字的宽高
        w, h = cv2.UMat.get(template).shape[::-1]
        # 身份证原图灰度图像的宽高
        img_w, img_h = cv2.UMat.get(img_gray).shape[::-1]
        # 加强匹配准确度，截取身份证图的下半部分图片
        Img = cv2.UMat.get(img_gray)[410:img_h, 0:img_w]

        # 找住址两个字的最佳匹配点
        res = cv2.matchTemplate(Img, template, cv2.TM_CCORR_NORMED)
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)  # max_loc代表匹配度最高的点的坐标（该店坐标是top_left坐标）

        # 计算人像图片的最底层的纵坐标
        target_y = max_loc[1] + int(500 * x)
        leftup = (0, target_y)
        rightdown = (img_w, target_y + int(30 * x))
        Img = cv2.UMat(Img)  # 格式转换
        bottom_image = cv2.UMat.get(Img)[target_y:target_y + int(200 * x), 0:img_w]
        bottom_image = cv2.UMat(bottom_image)
        # 二值化
        ret, photo = cv2.threshold(bottom_image, 80, 255, cv2.THRESH_BINARY)
        # 边缘检测
        blur = cv2.GaussianBlur(photo, (5, 5), 0)  # 用高斯滤波处理原图像降噪
        canny = cv2.Canny(blur, 50, 150)  # 50是最小阈值,150是最大阈值
        # Umat转换为array
        cannyarr = canny.get()
        # 存储检测到的边缘的像素点的横坐标，横坐标满足大于200（估值，身份证图片总宽1280，人脸图片大概的位置）并且值为255就存储起来，再在这个数组里面找横坐标最小的点，则可以找到轮廓的最边缘
        targetIndex = []
        for i in range(len(cannyarr)):
            for j in range(len(cannyarr[0])):
                if cannyarr[i][j] == 255 and j > 200:
                    targetIndex.append(j)
        # 最边缘的横坐标
        edgenode = min(targetIndex)
        # bottom_image = cv2.rectangle(canny, (807, 0), (1000, 20), (255, 255, 0), 1)
        # showing(bottom_image, "template_image")

        # 获取身份证号码年份最后一位的数字的中间位置
        # 公民身份号码的模板
        template = cv2.UMat(
            cv2.imread(r'E:/myvue/IDcard_recog/idcardocr_system_back/idcard_ocr/mask_img/idnum_mask_%s.jpg' % pixel_x,
                       0))
        w, h = cv2.UMat.get(template).shape[::-1]
        res = cv2.matchTemplate(img_gray, template, cv2.TM_CCOEFF_NORMED)
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)
        # 110 2160
        image = cv2.rectangle(img_gray, (max_loc[0] + w + int(1188 * x), max_loc[1]),
                              (max_loc[0] + w + int(1210 * x), max_loc[1] + int(200 * x)), (255, 255, 0), 1)
        midnode = max_loc[0] + w + int(1208 * x)
        # 差值小于15算正确
        tip = "false"
        if abs(edgenode - midnode) < 15:
            tip = "true"
        return tip

    @staticmethod
    def detect_id_mid(img):
        id6_mask = cv2.UMat(cv2.imread("E:/myvue/IDcard_recog/idcardocr_system_back/idcard_ocr/mask_img/id_mask.JPG"))
        id6_mask = img_resize_x(id6_mask)
        cv2.imwrite('E:/myvue/IDcard_recog/idcardocr_system_back/idcard_ocr/mask_img/id_mask_%s.jpg' % pixel_x,
                    id6_mask)
        img_gray, img_org = img_resize_gray(img)
        img_w, img_h = cv2.UMat.get(img_gray).shape[::-1]
        # 加强匹配准确度，截取身份证图的下半部分图片
        Img = cv2.UMat.get(img_gray)[650:img_h - 50, 0:img_w]
        template = cv2.UMat(
            cv2.imread(r'E:/myvue/IDcard_recog/idcardocr_system_back/idcard_ocr/mask_img/id6_mask_%s.jpg' % pixel_x,
                       0))

        res = cv2.matchTemplate(Img, template, cv2.TM_CCOEFF_NORMED)
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)

        image = cv2.rectangle(Img, (max_loc[0], max_loc[1]),
                              (max_loc[0] + int(100 * x), max_loc[1] + int(200 * x)), (255, 255, 0), 1)
        cv2.namedWindow("image", 0)
        cv2.imshow("image", image)
        cv2.waitKey(0)


def generate_mask(x):
    name_mask_pic = cv2.UMat(cv2.imread('name_mask.jpg'))
    sex_mask_pic = cv2.UMat(cv2.imread('sex_mask.jpg'))
    nation_mask_pic = cv2.UMat(cv2.imread('nation_mask.jpg'))
    birth_mask_pic = cv2.UMat(cv2.imread('birth_mask.jpg'))
    year_mask_pic = cv2.UMat(cv2.imread('year_mask.jpg'))
    month_mask_pic = cv2.UMat(cv2.imread('month_mask.jpg'))
    day_mask_pic = cv2.UMat(cv2.imread('day_mask.jpg'))
    address_mask_pic = cv2.UMat(cv2.imread('address_mask.jpg'))
    idnum_mask_pic = cv2.UMat(cv2.imread('idnum_mask.jpg'))
    name_mask_pic = img_resize_x(name_mask_pic)
    sex_mask_pic = img_resize_x(sex_mask_pic)
    nation_mask_pic = img_resize_x(nation_mask_pic)
    birth_mask_pic = img_resize_x(birth_mask_pic)
    year_mask_pic = img_resize_x(year_mask_pic)
    month_mask_pic = img_resize_x(month_mask_pic)
    day_mask_pic = img_resize_x(day_mask_pic)
    address_mask_pic = img_resize_x(address_mask_pic)
    idnum_mask_pic = img_resize_x(idnum_mask_pic)
    cv2.imwrite('name_mask_%s.jpg' % pixel_x, name_mask_pic)
    cv2.imwrite('sex_mask_%s.jpg' % pixel_x, sex_mask_pic)
    cv2.imwrite('nation_mask_%s.jpg' % pixel_x, nation_mask_pic)
    cv2.imwrite('birth_mask_%s.jpg' % pixel_x, birth_mask_pic)
    cv2.imwrite('year_mask_%s.jpg' % pixel_x, year_mask_pic)
    cv2.imwrite('month_mask_%s.jpg' % pixel_x, month_mask_pic)
    cv2.imwrite('day_mask_%s.jpg' % pixel_x, day_mask_pic)
    cv2.imwrite('address_mask_%s.jpg' % pixel_x, address_mask_pic)
    cv2.imwrite('idnum_mask_%s.jpg' % pixel_x, idnum_mask_pic)


# 用于生成模板
def img_resize_x(imggray):
    # print 'dheight:%s' % dheight
    crop = imggray
    size = crop.get().shape
    dheight = int(size[0] * x)
    dwidth = int(size[1] * x)
    crop = cv2.resize(src=crop, dsize=(dwidth, dheight), interpolation=cv2.INTER_CUBIC)
    return crop


# idcardocr里面resize以高度为依据, 用于get部分
def img_resize(imggray, dheight):
    # print 'dheight:%s' % dheight
    crop = imggray
    size = crop.get().shape
    height = size[0]
    width = size[1]
    width = width * dheight / height
    crop = cv2.resize(src=crop, dsize=(int(width), dheight), interpolation=cv2.INTER_CUBIC)
    return crop


def img_resize_gray(imgorg):
    # imgorg = cv2.imread(imgname)
    crop = imgorg
    size = cv2.UMat.get(crop).shape
    # print size
    height = size[0]
    width = size[1]
    # 参数是根据3840调的
    height = int(height * 3840 * x / width)
    # print height
    crop = cv2.resize(src=crop, dsize=(int(3840 * x), height), interpolation=cv2.INTER_CUBIC)
    return hist_equal(cv2.cvtColor(crop, cv2.COLOR_BGR2GRAY)), crop


def find_name(crop_gray, crop_org):
    # template = cv2.UMat(cv2.imread('idcard_ocr/mask_img/name_mask_%s.jpg' % pixel_x, 0))
    template = cv2.UMat(
        cv2.imread(r'E:/myvue/IDcard_recog/idcardocr_system_back/idcard_ocr/mask_img/name_mask_%s.jpg' % pixel_x,
                   0))  # template 得到姓名图片
    w, h = cv2.UMat.get(template).shape[::-1]
    res = cv2.matchTemplate(crop_gray, template, cv2.TM_CCOEFF_NORMED)
    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)
    # print(max_loc)
    top_left = (max_loc[0] + w, max_loc[1] - int(20 * x))
    bottom_right = (top_left[0] + int(700 * x), top_left[1] + int(300 * x))
    result = cv2.UMat.get(crop_org)[top_left[1] - 10:bottom_right[1], top_left[0] - 10:bottom_right[0]]
    cv2.rectangle(crop_gray, top_left, bottom_right, 255, 2)
    # showimg(result)
    return cv2.UMat(result)


'''
def find_sex(crop_gray, crop_org):
        template = cv2.UMat(cv2.imread('sex_mask_%s.jpg'%pixel_x, 0))
        # showimg(template)
        w, h = cv2.UMat.get(template).shape[::-1]
        res = cv2.matchTemplate(crop_gray, template, cv2.TM_CCOEFF_NORMED)
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)
        top_left = (max_loc[0] + w, max_loc[1] - int(20*x))
        bottom_right = (top_left[0] + int(300*x), top_left[1] + int(300*x))
        result = cv2.UMat.get(crop_org)[top_left[1]-10:bottom_right[1], top_left[0]-10:bottom_right[0]]
        cv2.rectangle(crop_gray, top_left, bottom_right, 255, 2)
        #showimg(crop_gray)
        return cv2.UMat(result)
'''


def find_nation(crop_gray, crop_org):
    template = cv2.UMat(
        cv2.imread(r'E:/myvue/IDcard_recog/idcardocr_system_back/idcard_ocr/mask_img/nation_mask_%s.jpg' % pixel_x, 0))
    w, h = cv2.UMat.get(template).shape[::-1]
    res = cv2.matchTemplate(crop_gray, template, cv2.TM_CCOEFF_NORMED)
    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)
    top_left = (max_loc[0] + w - int(20 * x), max_loc[1] - int(20 * x))
    bottom_right = (top_left[0] + int(500 * x), top_left[1] + int(300 * x))
    nation_result = cv2.UMat.get(crop_org)[top_left[1] - 10:bottom_right[1], top_left[0] - 10:bottom_right[0]]
    cv2.rectangle(crop_gray, top_left, bottom_right, 255, 2)
    # showing(cv2.UMat(result),'3')
    return cv2.UMat(nation_result)


# def find_birth(crop_gray, crop_org):
#         template = cv2.UMat(cv2.imread('birth_mask_%s.jpg'%pixel_x, 0))
#         # showimg(template)
#         w, h = cv2.UMat.get(template).shape[::-1]
#         res = cv2.matchTemplate(crop_gray, template, cv2.TM_CCOEFF_NORMED)
#         #showimg(crop_gray)
#         min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)
#         top_left = (max_loc[0] + w, max_loc[1] - int(20*x))
#         bottom_right = (top_left[0] + int(1500*x), top_left[1] + int(300*x))
#         # 提取result需要在rectangle之前
#         date_org = cv2.UMat.get(crop_org)[top_left[1]:bottom_right[1], top_left[0]:bottom_right[0]]
#         date = cv2.cvtColor(date_org, cv2.COLOR_BGR2GRAY)
#         cv2.rectangle(crop_gray, top_left, bottom_right, 255, 2)
#         # cv2.imwrite('date.png',date)
#
#         # 提取年份
#         template = cv2.UMat(cv2.imread('year_mask_%s.jpg'%pixel_x, 0))
#         year_res = cv2.matchTemplate(date, template, cv2.TM_CCOEFF_NORMED)
#         min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(year_res)
#         bottom_right = (max_loc[0]+int(20*x), int(300*x))
#         top_left = (0, 0)
#         year = date_org[top_left[1]:bottom_right[1], top_left[0]:bottom_right[0]]
#         # cv2.imwrite('year.png',year)
#         cv2.rectangle(crop_gray, top_left, bottom_right, 255, 2)
#
#         # 提取月
#         template = cv2.UMat(cv2.imread('month_mask_%s.jpg'%pixel_x, 0))
#         month_res = cv2.matchTemplate(date, template, cv2.TM_CCOEFF_NORMED)
#         min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(month_res)
#         bottom_right = (max_loc[0]+int(40*x), int(300*x))
#         top_left = (max_loc[0] - int(220*x), 0)
#         month = date_org[top_left[1]:bottom_right[1], top_left[0]:bottom_right[0]]
#         # cv2.imwrite('month.png',month)
#         cv2.rectangle(crop_gray, top_left, bottom_right, 255, 2)
#
#         # 提取日
#         template = cv2.UMat(cv2.imread('day_mask_%s.jpg'%pixel_x, 0))
#         day_res = cv2.matchTemplate(date, template, cv2.TM_CCOEFF_NORMED)
#         min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(day_res)
#         bottom_right = (max_loc[0]+int(20*x), int(300*x))
#         top_left = (max_loc[0] - int(220*x), 0)
#         day = date_org[top_left[1]:bottom_right[1], top_left[0]:bottom_right[0]]
#         # cv2.imwrite('day.png',day)
#         cv2.rectangle(crop_gray, top_left, bottom_right, 255, 2)
#         showimg(crop_gray)
#         return cv2.UMat(year), cv2.UMat(month), cv2.UMat(day)

def find_address(crop_gray, crop_org):
    template = cv2.UMat(
        cv2.imread(r'E:/myvue/IDcard_recog/idcardocr_system_back/idcard_ocr/mask_img/address_mask_%s.jpg' % pixel_x, 0))
    w, h = cv2.UMat.get(template).shape[::-1]

    img_w, img_h = cv2.UMat.get(crop_gray).shape[::-1]
    crop_gray = cv2.UMat.get(crop_gray)[410:img_h, 0:img_w]
    crop_org = cv2.UMat.get(crop_org)[410:img_h, 0:img_w]

    res = cv2.matchTemplate(crop_gray, template, cv2.TM_CCORR_NORMED)

    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)  # max_loc代表匹配度最高的点的坐标（该店坐标是top_left坐标）
    # template_top_left = max_loc  # 地址模板左上点坐标
    # tempalte_bottom_right = (template_top_left[0]+w,template_top_left[1]+h)  # 右下带你坐标
    # template_image = cv2.rectangle(crop_gray, template_top_left, tempalte_bottom_right, 255,1)
    # showing(template_image, "template_image")

    top_left = (max_loc[0] + w, max_loc[1])  # 计算得到地址栏左上坐标
    bottom_right = (top_left[0] + int(1700 * x), top_left[1] + int(700 * x))  # 计算得到地址栏右下坐标
    addr_result = crop_org[top_left[1]:bottom_right[1], top_left[0]:bottom_right[0]]  # 得到地址栏剪裁结果
    # image_test=cv2.rectangle(template_image, top_left, bottom_right, 255,1)
    # showing(image_test,"test")
    # 身份证真伪验证——地址栏第一行11个字验证，剪切地址栏第一行，top_left的坐标已经有了，只需要计算地址栏第一行的 bottom_right
    firline_bottom_right = (top_left[0] + int(1700 * x), top_left[1] + int(200 * x))
    firline_result = crop_org[top_left[1]:firline_bottom_right[1], top_left[0]:firline_bottom_right[0]]  # 得到地址栏第一行剪裁结果

    # showing(addr_result, "addr_result")
    # cv2.imshow("result", addr_result)

    return cv2.UMat(addr_result), cv2.UMat(firline_result)


def find_idnum(crop_gray, crop_org):
    template = cv2.UMat(
        cv2.imread(r'E:/myvue/IDcard_recog/idcardocr_system_back/idcard_ocr/mask_img/idnum_mask_%s.jpg' % pixel_x, 0))
    # showimg(template)
    # showimg(crop_gray)
    w, h = cv2.UMat.get(template).shape[::-1]
    res = cv2.matchTemplate(crop_gray, template, cv2.TM_CCOEFF_NORMED)
    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)
    top_left = (max_loc[0] + w, max_loc[1] - int(20 * x))
    bottom_right = (top_left[0] + int(2300 * x), top_left[1] + int(300 * x))
    idnum_result = cv2.UMat.get(crop_org)[top_left[1] - 10:bottom_right[1], top_left[0] - 10:bottom_right[0]]
    # cv2.rectangle(crop_gray, top_left, bottom_right, 255, 2)
    # showimg(crop_gray)
    return cv2.UMat(idnum_result)


def showing(img, name):
    # cv2.namedWindow("contours", 0);
    # cv2.resizeWindow("contours", 1280, 720);
    # cv2.imshow("contours", img)
    # cv2.waitKey()
    cv2.namedWindow(name, 0)
    cv2.resizeWindow(name, 1280, 720)
    cv2.imshow(name, img)
    cv2.waitKey(0)  # 等待键盘按键


# psm model:
#  0    Orientation and script detection (OSD) only.
#  1    Automatic page segmentation with OSD.    
#  2    Automatic page segmentation, but no OSD, or OCR.
#  3    Fully automatic page segmentation, but no OSD. (Default)
#  4    Assume a single column of text of variable sizes.
#  5    Assume a single uniform block of vertically aligned text.
#  6    Assume a single uniform block of text.
#  7    Treat the image as a single text line.
#  8    Treat the image as a single word.
#  9    Treat the image as a single word in a circle.
#  10    Treat the image as a single character.
#  11    Sparse text. Find as much text as possible in no particular order.
#  12    Sparse text with OSD.
#  13    Raw line. Treat the image as a single text line,
# 			bypassing hacks that are Tesseract-specific

def get_name(img, name_handle):
    print('name')
    _, _, red = cv2.split(img)  # split 会自动将UMat转换回Mat   img彩色的，red单通道图片灰色的
    red = cv2.UMat(red)
    red = hist_equal(red)
    # red1 = cv2.adaptiveThreshold(red, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY, 151, 50)#二值化
    red = cv2.adaptiveThreshold(red, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 151, 55)  # 二值化
    #    red = cv2.medianBlur(red, 3)
    # red = img_resize(red, 150)#白底黑字调整大小
    img = img_resize(img, 150)  # 原图调整大小（数字越小，细节更加明显）
    # showing(img, 'name-img')
    # showing(red1,'name-mean')
    # showing(red,'name-gaussian')
    name = get_result_vary_length(red, name_handle, 'chi_sim', img, '--psm 7')
    print(name)
    return name
    # return punc_filter(pytesseract.image_to_string(img, lang='chi_sim', config='-psm 13').replace(" ",""))


def get_address(img, addr_handle):
    print('address')
    _, _, red = cv2.split(img)
    red = cv2.UMat(red)
    red = hist_equal(red)
    # showing(red,'red0')
    # red=cv2.bilateralFilter(red,0,s,d)
    # red=cv2.ximgproc.guidedFilter(red,red,50,20,-5)
    # showing(red,'red1')
    red = cv2.adaptiveThreshold(red, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 135, 40)

    # print(pytesseract.image_to_string(red, lang='chi_sim', config='-psm 6'))
    # red=cv2.dilate(red,np.ones((3,3),np.uint8),1)
    # red=cv2.erode(red,np.ones((5,5),np.uint8),3)
    # red = cv2.medianBlur(red,3)
    # red=cv2.GaussianBlur(red, (3, 3),200)#高斯滤波
    # red=cv2.boxFilter(red, -1, (3, 3), normalize =1)#方框滤波，效果差
    # red=cv2.blur(red, (3, 3))#均值滤波

    # showing(red,'red2')
    red = img_resize(red, 300)
    img = img_resize(img, 300)
    address = punc_filter(get_result_vary_length(red, addr_handle, 'chi_sim', img, '--psm 6'))
    print(address)
    return address
    # return punc_filter(pytesseract.image_to_string(img, lang='chi_sim', config='-psm 3').replace(" ",""))


def new_get_sex(id0):
    judge_num = int(id0[-2])
    if judge_num % 2 == 0:
        sex = "女"
    else:
        sex = "男"
    print("sex")
    print(sex)
    return sex


'''
def get_sex(img,handle):
        _, _, red = cv2.split(img)
        print('sex')
        red = cv2.UMat(red)
        #showing(red,"name1")
        red = hist_equal(red)
        #showing(red,"name2")
        red = cv2.adaptiveThreshold(red, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 151, 50)
        #showing(red,"name3")
        #    red = cv2.medianBlur(red, 3)
        #    cv2.imwrite('address.png', img)
        #    img2 = Image.open('address.png')
        red = img_resize(red, 150)
        
        
        # cv2.imwrite('sex.png', red)
        # img = Image.fromarray(cv2.UMat.get(red).astype('uint8'))
        #return get_result_fix_length(red, 1, 'sex', '-psm 10')
        return get_result_fix_length(red,handle, 1, 'chi_sim', '--psm 10')
        # return pytesseract.image_to_string(img, lang='sex', config='-psm 10').replace(" ","")
'''


def get_nation(img, nation_handle):
    _, _, red = cv2.split(img)
    print('nation')
    red = cv2.UMat(red)
    red = hist_equal(red)
    red = cv2.adaptiveThreshold(red, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 151, 46)
    red = img_resize(red, 300)
    img = img_resize(img, 300)
    # img = Image.fromarray(cv2.UMat.get(red).astype('uint8'))
    # cv2.imwrite('nation.png', red)
    new_nation = get_result_fix_length(red, nation_handle, img, 1, 'chi_sim', '--psm 10')
    last = new_nation[1:]
    if not last.isspace():
        print(new_nation)
        return new_nation
    new_nation = new_nation[0]
    if new_nation == '汊':
        new_nation = "汉"
    print(new_nation)
    return new_nation
    # return get_result_vary_length(red, 'chi_sim', img, '--psm 6')
    # return pytesseract.image_to_string(img, lang='chi_sim', config='--psm 13').replace(" ","")


# def get_birth(year, month, day):
#         _, _, red = cv2.split(year)
#         red = cv2.UMat(red)
#         red = hist_equal(red)
#         red = cv2.adaptiveThreshold(red, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 151, 50)
#         red = img_resize(red, 150)
#         # cv2.imwrite('year_red.png', red)
#         year_red = red
#
#         _, _, red = cv2.split(month)
#         red = cv2.UMat(red)
#         red = hist_equal(red)
#         red = cv2.adaptiveThreshold(red, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 151, 50)
#         #red = cv2.erode(red,kernel,iterations = 1)
#         red = img_resize(red, 150)
#         # cv2.imwrite('month_red.png', red)
#         month_red = red
#
#         _, _, red = cv2.split(day)
#         red = cv2.UMat(red)
#         red = hist_equal(red)
#         red = cv2.adaptiveThreshold(red, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 151, 50)
#         red = img_resize(red, 150)
#         # cv2.imwrite('day_red.png', red)
#         day_red = red
#         # return pytesseract.image_to_string(img, lang='birth', config='-psm 7')
#         return get_result_fix_length(year_red, 4, 'eng', '-c tessedit_char_whitelist=0123456789 -psm 13'), \
#                get_result_vary_length(month_red, 'eng', '-c tessedit_char_whitelist=0123456789 -psm 13'), \
#                get_result_vary_length(day_red, 'eng', '-c tessedit_char_whitelist=0123456789 -psm 13')


def get_idnum_and_birth(img, id_handle_num):
    _, _, red = cv2.split(img)
    red = cv2.UMat(red)
    red = hist_equal(red)
    red = cv2.adaptiveThreshold(red, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 151, 50)
    red = img_resize(red, 150)
    # cv2.imwrite('idnum_red.png', red)
    # idnum_str = get_result_fix_length(red, 18, 'idnum', '-psm 8')
    # idnum_str = get_result_fix_length(red, 18, 'eng', '--psm 8 ')
    img = Image.fromarray(cv2.UMat.get(red).astype('uint8'))
    idnum_str = get_result_vary_length(red, id_handle_num, 'eng', img, '--psm 8 ')
    return idnum_str, idnum_str[6:14]


def get_result_fix_length(red, fix_handle, img, fix_length, langset, custom_config=''):
    red_org = red  # red是黑白的

    cv2.fastNlMeansDenoising(red, red, 4, 7, 35)  # 非局部平均去噪
    rec, red = cv2.threshold(red, 127, 255, cv2.THRESH_BINARY_INV)  # 二值化
    image, contours, hierarchy = cv2.findContours(red, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    # print(len(contours))
    # 描边一次可以减少噪点
    cv2.drawContours(red, contours, -1, (0, 255, 0), 1)

    h_threshold = 54
    numset_contours = []
    calcu_cnt = 1
    for cnt in contours:
        x, y, w, h = cv2.boundingRect(cnt)
        if h > h_threshold:
            numset_contours.append((x, y, w, h))
    while len(numset_contours) != fix_length:
        if calcu_cnt > 50:
            new_nation = get_result_vary_length(red, fix_handle, 'chi_sim', img, '--psm 6')
            return new_nation
            break
        numset_contours = []
        calcu_cnt += 1
        if len(numset_contours) > fix_length:
            h_threshold += 1
            contours_cnt = 0
            for cnt in contours:
                x, y, w, h = cv2.boundingRect(cnt)
                if h > h_threshold:
                    contours_cnt += 1
                    numset_contours.append((x, y, w, h))
        if len(numset_contours) < fix_length:
            h_threshold -= 1
            contours_cnt = 0
            for cnt in contours:
                xx, y, w, h = cv2.boundingRect(cnt)
                if h > h_threshold:
                    contours_cnt += 1
                    numset_contours.append((xx, y, w, h))
    # imgrect = cv2.rectangle(color_img, (x, y), (x + w, y + h), (0, 255, 0), 2)
    # showing(imgrect,'imgrect')

    result_string = ''
    numset_contours.sort(key=lambda num: num[0])
    for xx, y, w, h in numset_contours:
        image2 = cv2.UMat.get(red_org)[y - 10:y + h + 10, xx - 20:xx + w + 10]

        imashow.imsave('E:/myvue/IDcard_recog/idcardocr_system_back/idcard_ocr/testimages/民族.jpg', image2)
        image2 = Image.open('E:/myvue/IDcard_recog/idcardocr_system_back/idcard_ocr/testimages/民族.jpg')
        tesseract_raw.set_image(fix_handle, image2)
        result_string = tesseract_raw.get_utf8_text(fix_handle)

    return result_string


def get_result_vary_length(red, vary_handle, langset, org_img, custom_config=''):
    # red:二值图片；langset：中文转换；org_img:原图；custom_config:转换模式
    red_org = red
    # cv2.namedWindow("name", 0)
    # cv2.imshow("name", red_org)
    # cv2.waitKey(0)
    rec, red = cv2.threshold(red, 127, 255, cv2.THRESH_BINARY_INV)
    image, contours, hierarchy = cv2.findContours(red, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

    # 描边一次可以减少噪点
    cv2.drawContours(red, contours, -1, (255, 255, 255), 1)
    # red=cv2.erode(red,np.ones((2,2),np.uint8),3)
    # color_img = cv2.cvtColor(red, cv2.COLOR_GRAY2BGR)

    # numset_contours = []
    height_list = []
    width_list = []
    for cnt in contours:
        xx, y, w, h = cv2.boundingRect(cnt)
        height_list.append(h)
        # print(h,w)
        width_list.append(w)

    height_list.remove(max(height_list))
    width_list.remove(max(width_list))
    height_threshold = 0.21 * max(height_list)  # 原来的阈值是0.7去乘，但是阈值高导致有的字检测不到
    width_threshold = 1.4 * max(width_list)
    # print('height_threshold:'+str(height_threshold)+'width_threshold:'+str(width_threshold))
    big_rect = []
    for cnt in contours:
        # print(cnt)
        # area = cv2.contourArea(cnt)
        # print("面积是：%s"%area)
        xx, yy, w, h = cv2.boundingRect(cnt)
        if h > height_threshold and w < width_threshold:  # 名字有几个字，就有几个符合条件
            # print(h,w)
            # numset_contours.append((x, y, w, h))
            big_rect.append((xx, yy))
            big_rect.append((xx + w, yy + h))

    big_rect_nparray = np.array(big_rect, ndmin=3)  # 转换成为3维的

    xx, y, w, h = cv2.boundingRect(big_rect_nparray)
    # imgrect = cv2.rectangle(color_img, (x, y), (x + w, y + h), (0, 255, 0), 2)
    # imgrect=cv2.erode(imgrect,np.ones((4,4),np.uint8),1)
    # showing(imgrect,'imgrect')
    result_string = ''

    image2 = cv2.UMat.get(red_org)[y - 10:y + h + 10, xx - 10:xx + w + 10]

    imashow.imsave('E:/myvue/IDcard_recog/idcardocr_system_back/idcard_ocr/testimages/ttest.jpg', image2)

    image2 = Image.open('E:/myvue/IDcard_recog/idcardocr_system_back/idcard_ocr/testimages/ttest.jpg')

    # cv2.namedWindow("识别输入", 0)
    # cv2.imshow("识别输入", image2)
    # cv2.waitKey()
    tesseract_raw.set_image(vary_handle, image2)
    result_string = tesseract_raw.get_utf8_text(vary_handle)

    return punc_filter(result_string)


def punc_filter(str1):
    temp = str1
    xx = u"([\u4e00-\u9fff0-9A-Z]+)"
    pattern = re.compile(xx)
    results = pattern.findall(temp)
    string = ""
    for res0 in results:
        string += res0
        # string = '%s%s' % (string, result)
    return string


# 这里使用直方图拉伸，不是直方图均衡
def hist_equal(img):
    # clahe_size = 8
    # clahe = cv2.createCLAHE(clipLimit=1.0, tileGridSize=(clahe_size, clahe_size))
    # result = clahe.apply(img)
    # test

    # result = cv2.equalizeHist(img)

    image = img.get()  # UMat to Mat
    # result = cv2.equalizeHist(image)
    lut = np.zeros(256, dtype=image.dtype)  # 创建空的查找表
    # lut = np.zeros(256)
    hist = cv2.calcHist([image],  # 计算图像的直方图
                        [0],  # 使用的通道
                        None,  # 没有使用mask
                        [256],  # it is a 1D histogram
                        [0, 256])
    minBinNo, maxBinNo = 0, 255
    # 计算从左起第一个不为0的直方图柱的位置
    for binNo, binValue in enumerate(hist):
        if binValue != 0:
            minBinNo = binNo
            break
    # 计算从右起第一个不为0的直方图柱的位置
    for binNo, binValue in enumerate(reversed(hist)):
        if binValue != 0:
            maxBinNo = 255 - binNo
            break
    # print minBinNo, maxBinNo
    # 生成查找表
    for i, v in enumerate(lut):
        if i < minBinNo:
            lut[i] = 0
        elif i > maxBinNo:
            lut[i] = 255
        else:
            lut[i] = int(255.0 * (i - minBinNo) / (maxBinNo - minBinNo) + 0.5)
    # 计算,调用OpenCV cv2.LUT函数,参数 image --  输入图像，lut -- 查找表
    # print lut
    result1 = cv2.LUT(image, lut)
    # print type(result)
    # showimg(result)
    return cv2.UMat(result1)


if __name__ == "__main__":
    handle = tesseract_raw.init(lang='chi_sim')
    handle_num = tesseract_raw.init(lang='eng')
    path = r'E:/myvue/IDcard_recog/idcardocr_system_back/idcard_ocr/testimages/1.jpg'
    # idcard_recognize.process(path)
    idfind = findidcard.Findidcard()
    idcard_img = idfind.find(path)  # 对图像进行校正处理
    # cv2.imshow('dd', idcard_img)
    # cv2.waitKey()

    result = idcardocr(idcard_img, handle, handle_num)
