# -*- coding: utf-8 -*-
"""
Created on Wed Mar 24 15:42:55 2021

@author: dell
"""

# -*- coding: utf-8 -*-
from PIL import Image
# import pytesseract
import cv2
import numpy as np
import re
# from multiprocessing import Pool, Queue, Lock, Process, freeze_support
# import time
# import matplotlib.pyplot as plt
import matplotlib

import idcard_recognize
import compare
import time

from pyocr.libtesseract import tesseract_raw

# pytesseract.pytesseract.tesseract_cmd = 'C:\\Program Files (x86)\\Tesseract-OCR\\tesseract.exe'
x = 1280.00 / 3840.00
pixel_x = int(x * 3840)
print(x, pixel_x)


# mode0:识别姓名，出生日期，身份证号； mode1：识别所有信息
# s和d是为了训练参数用到的，实际不需要
def idcardocr(imgname, handle, handle_num, mode=1):
    print(u'进入身份证光学识别流程...')

    img_data_gray, img_org = img_resize_gray(imgname)  # img_data_gray身份证灰度图像，img_org身份证彩色图像
    result_dict = dict()
    t1 = round(time.time() * 1000)
    address_pic = find_nation(img_data_gray, img_org)
    result_dict['nation'] = get_nation(address_pic, handle)
    t2 = round(time.time() * 1000)
    print("计算时间为%s" % (t2 - t1))

    return result_dict


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


def find_nation(crop_gray, crop_org):
    template = cv2.UMat(cv2.imread('nation_mask_%s.jpg' % pixel_x, 0))
    w, h = cv2.UMat.get(template).shape[::-1]
    res = cv2.matchTemplate(crop_gray, template, cv2.TM_CCOEFF_NORMED)
    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)
    top_left = (max_loc[0] + w - int(20 * x), max_loc[1] - int(20 * x))
    # top_left = (max_loc[0] + w-int(20*x), max_loc[1]- int(30*x))
    bottom_right = (top_left[0] + int(700 * x), top_left[1] + int(300 * x))
    # bottom_right = (top_left[0] + int(500*x), top_left[1] + h+int(100*x))

    result = cv2.UMat.get(crop_org)[top_left[1] - 10:bottom_right[1], top_left[0] - 10:bottom_right[0]]
    # result = cv2.UMat.get(crop_org)[top_left[1]:bottom_right[1], top_left[0]:bottom_right[0]]
    # cv2.rectangle(crop_gray, top_left, bottom_right, 255, 2)

    result = cv2.UMat(result)
    # cv2.imshow("result",result)
    return result


def showing(img, name):
    cv2.namedWindow(name, 0)
    cv2.resizeWindow(name, 1280, 720)
    cv2.imshow(name, img)
    # cv2.waitKey(0)#等待键盘按键


def get_nation(img, handle):
    _, _, red = cv2.split(img)
    print('nation')
    red = cv2.UMat(red)
    red = hist_equal(red)
    red = cv2.adaptiveThreshold(red, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 151, 46)
    red = img_resize(red, 300)
    img = img_resize(img, 300)
    # img = Image.fromarray(cv2.UMat.get(red).astype('uint8'))
    cv2.imwrite('testimages/nation.jpg', red)
    # matplotlib.image.imsave('testimages/nation_mask.jpg',img)

    # 对比

    nation_mask = r"testimages/nation_mask.jpg"
    nation_now = r"testimages/nation.jpg"
    comp_value = compare.similarity(nation_mask, nation_now)
    if (comp_value > 0.11):
        new_nation = "汉"
    else:
        new_nation = get_result_fix_length(red, handle, img, 1, 'chi_sim', '--psm 10')
    '''
        new_nation=get_result_fix_length(red,handle,img,1,'chi_sim', '--psm 10')
        '''

    last = new_nation[1:]
    if (last.isspace() != True):
        print(new_nation)
        return new_nation
    new_nation = new_nation[0]
    if (new_nation == '汊'):
        new_nation = "汉"
    print(new_nation)
    return new_nation


def get_result_fix_length(red, handle, img, fix_length, langset, custom_config=''):
    red_org = red  # red是黑白的
    cv2.fastNlMeansDenoising(red, red, 4, 7, 35)  # 非局部平均去噪
    rec, red = cv2.threshold(red, 127, 255, cv2.THRESH_BINARY_INV)  # 二值化
    image, contours, hierarchy = cv2.findContours(red, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

    """
    color_img = cv2.cvtColor(red, cv2.COLOR_GRAY2BGR)
    for x, y, w, h in contours:
         imgrect = cv2.rectangle(color_img, (x, y), (x + w, y + h), (0, 255, 0), 2)
    cv2.imshow("imgrect",imgrect)
    """
    h_threshold = 54
    numset_contours = []
    calcu_cnt = 1
    for cnt in contours:
        x, y, w, h = cv2.boundingRect(cnt)
        if h > h_threshold:
            numset_contours.append((x, y, w, h))
    print(numset_contours)
    while len(numset_contours) != fix_length:
        if calcu_cnt > 50:
            new_nation = get_result_vary_length(red, handle, 'chi_sim', img, '--psm 6')
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
                x, y, w, h = cv2.boundingRect(cnt)
                if h > h_threshold:
                    contours_cnt += 1
                    numset_contours.append((x, y, w, h))
    # imgrect = cv2.rectangle(color_img, (x, y), (x + w, y + h), (0, 255, 0), 2)
    # showing(imgrect,'imgrect')

    result_string = ''
    numset_contours.sort(key=lambda num: num[0])

    for x, y, w, h in numset_contours:
        image2 = cv2.UMat.get(red_org)[y - 10:y + h + 10, x - 20:x + w + 10]

        matplotlib.image.imsave('testimages/民族.jpg', image2)
        image2 = Image.open('testimages/民族.jpg')
        tesseract_raw.set_image(handle, image2)
        result_string = tesseract_raw.get_utf8_text(handle)

        # result_string += pytesseract.image_to_string(image2, lang=langset, config=custom_config)
    # print('结果是：'+ result_string)
    # showing(cv2.UMat.get(red_org)[y-10:y + h + 10, x-10:x + w + 10],'no9')
    # print(new_r)
    # cv2.imwrite('fixlengthred.png', cv2.UMat.get(red_org)[y-10:y + h +10 , x-10:x + w + 10])
    # print(result_string)
    return result_string


def get_result_vary_length(red, handle, langset, org_img, custom_config=''):
    # red:二值图片；langset：中文转换；org_img:原图；custom_config:转换模式
    red_org = red
    rec, red = cv2.threshold(red, 127, 255, cv2.THRESH_BINARY_INV)
    image, contours, hierarchy = cv2.findContours(red, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

    # 描边一次可以减少噪点
    cv2.drawContours(red, contours, -1, (255, 255, 255), 1)
    # red=cv2.erode(red,np.ones((2,2),np.uint8),3)
    color_img = cv2.cvtColor(red, cv2.COLOR_GRAY2BGR)

    # numset_contours = []
    height_list = []
    width_list = []
    for cnt in contours:
        x, y, w, h = cv2.boundingRect(cnt)
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
        x, y, w, h = cv2.boundingRect(cnt)
        if h > height_threshold and w < width_threshold:  # 名字有几个字，就有几个符合条件
            # print(h,w)
            # numset_contours.append((x, y, w, h))
            big_rect.append((x, y))
            big_rect.append((x + w, y + h))

    big_rect_nparray = np.array(big_rect, ndmin=3)  # 转换成为3维的

    x, y, w, h = cv2.boundingRect(big_rect_nparray)
    imgrect = cv2.rectangle(color_img, (x, y), (x + w, y + h), (0, 255, 0), 2)
    # imgrect=cv2.erode(imgrect,np.ones((4,4),np.uint8),1)
    # showing(imgrect,'imgrect')
    result_string = ''
    # cv2.imshow("red_org",red_org)
    image2 = cv2.UMat.get(red_org)[y:y + h + 10, x:x + w + 10]

    matplotlib.image.imsave('testimages/ttest.jpg', image2)
    image2 = Image.open('testimages/ttest.jpg')
    tesseract_raw.set_image(handle, image2)
    result_string = tesseract_raw.get_utf8_text(handle)

    # result_string = pytesseract.image_to_string(image2, lang=langset,config=custom_config)
    # numset_contours.sort(key=lambda num: num[0])
    # for x, y, w, h in numset_contours:
    #     result_string += pytesseract.image_to_string(cv2.UMat.get(color_img)[y:y + h, x:x + w], lang=langset, config=custom_config)
    return punc_filter(result_string)


def punc_filter(str):
    temp = str
    xx = u"([\u4e00-\u9fff0-9A-Z]+)"
    pattern = re.compile(xx)
    results = pattern.findall(temp)
    string = ""
    for result in results:
        string += result
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
    result = cv2.LUT(image, lut)
    # print type(result)
    # showimg(result)
    return cv2.UMat(result)


if __name__ == "__main__":
    # idocr = idcardocr(cv2.UMat(cv2.imread('testimages/zrh.jpg')))
    # print(idocr)
    # for i in range(15):
    #     idocr = idcardocr(cv2.UMat(cv2.imread('testimages/%s.jpg'%(i+1))))
    #     print(idocr['idnum'])
    # idcard_recognize.process('testimages/2.jpg')
    # idcard_recognize.process('testimages/5.jpg')
    # print(idcard_recognize.process('testimages/line3_addre.jpg'))
    # print(idcard_recognize.process('testimages/light1.jpg'))
    print(idcard_recognize.process('testimages/1.jpg'))
