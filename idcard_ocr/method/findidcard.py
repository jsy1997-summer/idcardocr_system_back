# -*- coding: utf-8 -*-
import numpy as np
import cv2
import time


class Findidcard:
    def __init__(self):
        pass

    # img1为身份证模板, img2为需要识别的图像
    def find(self, img2_name):
        print(u'进入身份证模版匹配流程...')
        t1 = round(time.time() * 1000)
        # img1_name = 'idcard_ocr/mask_img/idcard_mask.jpg'
        img1_name = r"E:/myvue/IDcard_recog/idcardocr_system_back/idcard_ocr/mask_img/idcard_mask.jpg"
        MIN_MATCH_COUNT = 10
        # imagetest = cv2.imread(img1_name, 0)
        # print(type(imagetest))#numpy.ndarray
        img1 = cv2.UMat(cv2.imread(img1_name, 0))  # queryImage in GrayUMatU型难找最好的硬件，提升性能
        # print(type(img1))#cv2.UMat
        img1 = self.img_resize(img1, 640)
        # img1 = idocr.hist_equal(img1)
        img2 = cv2.UMat(cv2.imread(img2_name, 0))  # trainImage in Gray加载灰度图像
        # img2 = cv2.cvtColor(img2_name, cv2.COLOR_BGR2GRAY)
        # img2 = cv2.UMat(img2)
        # self.showimg(img2, 'img2')
        # print(img2.get().shape)
        img2 = self.img_resize(img2, 1920)
        # img2 = idocr.hist_equal(img2)
        img_org = cv2.UMat(cv2.imread(img2_name))  # 加载彩色图像
        # img_org = cv2.UMat(img2_name)  # 加载彩色图像
        img_org = self.img_resize(img_org, 1920)  #
        #  Initiate SIFT detector
        sift = cv2.xfeatures2d.SIFT_create()
        # find the keypoints and descriptors with SIFT
        kp1, des1 = sift.detectAndCompute(img1, None)
        kp2, des2 = sift.detectAndCompute(img2, None)

        FLANN_INDEX_KDTREE = 0
        index_params = dict(algorithm=FLANN_INDEX_KDTREE, trees=5)
        search_params = dict(checks=10)

        # 创建特征匹配器
        flann = cv2.FlannBasedMatcher(index_params, search_params)
        matches = flann.knnMatch(des1, des2, k=2)  # k=2表示在测试图片上返回两个与样本图片匹配的点
        # for m, n in matches:
        #     print(m)
        #     print(m.queryIdx)
        #     print(m.trainIdx)
        #     print(m.distance)
        #     print(n)
        #     print(n.queryIdx)
        #     print(n.trainIdx)
        #     print(n.distance)
        # queryIdx：测试图像的特征点描述符的下标（第几个特征点描述符），同时也是描述符对应特征点的下标。
        # trainIdx：样本图像的特征点描述符下标, 同时也是描述符对应特征点的下标。
        # distance：代表这怡翠匹配的特征点描述符的欧式距离，数值越小也就说明俩个特征点越相近。

        # store all the good matches as per Lowe's ratio test.
        # 两个最佳匹配之间距离需要大于ratio 0.7,距离过于相似可能是噪声点
        good = []  # 最佳的匹配点
        for m, n in matches:
            if m.distance < 0.7 * n.distance:
                good.append(m)
        # m表示大图像上最匹配点的距离，n表示次匹配点的距离，比值越小证明特征点越明显

        # reshape为(x,y)数组
        # 绘制的参数，匹配连线的颜色，特征点的颜色，需要画哪些匹配，flags=0绘制点和线，=2不画特征点
        # good = np.expand_dims(good, 1)
        # drawParams = dict(matchColor=(0, 0, 255), singlePointColor=(255, 0, 0))  # 给特征点和匹配的线定义颜色
        # resultimage = cv2.drawMatchesKnn(img1, kp1, img2, kp2, matches, None, **drawParams)
        #
        # self.showimg(resultimage, 'pipei')  # 特征点匹配结果

        if len(good) > MIN_MATCH_COUNT:
            src_pts = np.float32([kp1[m.queryIdx].pt for m in good]).reshape(-1, 1, 2)  # 获取测试图片上的关键点的坐标

            dst_pts = np.float32([kp2[m.trainIdx].pt for m in good]).reshape(-1, 1, 2)   # 获取样本图片上的关键点的坐标

            # 用HomoGraphy计算图像与图像之间映射关系, M为转换矩阵
            M, mask = cv2.findHomography(src_pts, dst_pts, cv2.RANSAC, 5.0)  # 计算多个二维点对之间的最优单映射变换矩阵 H（3行x3列）
            print(M)
            matchesMask = mask.ravel().tolist()

            # 使用转换矩阵M计算出img1在img2的对应形状
            h, w = cv2.UMat.get(img1).shape
            M_r = np.linalg.inv(M)
            im_r = cv2.warpPerspective(img_org, M_r, (w, h))
            # im_r = cv2.perspectiveTransform(img_org, M)
            # self.showimg(im_r)
        else:
            print("Not enough matches are found - %d/%d" % (len(good), MIN_MATCH_COUNT))
            matchesMask = None

        # draw_params = dict(matchColor = (0,255,0), # draw matches in green color
        #           singlePointColor = None,
        #           matchesMask = matchesMask, # draw only inliers
        #           flags = 2)
        # img3 = cv2.drawMatches(img1,kp1,img2,kp2,good,None,**draw_params)
        # plt.imshow(img3, 'gray'),plt.show()
        t2 = round(time.time() * 1000)
        print(u'查找身份证耗时:%s' % (t2 - t1))
        # self.showimg(im_r,"correct_to_img")
        return im_r

    @staticmethod
    def showimg(img, name):
        cv2.namedWindow(name, 0)
        cv2.resizeWindow("contours", 1600, 1200);
        cv2.imshow(name, img)
        cv2.waitKey()

    @staticmethod
    def img_resize(imggray, dwidth):
        # print 'dwidth:%s' % dwidth
        crop = imggray
        size = crop.get().shape
        height = size[0]
        width = size[1]
        height = height * dwidth / width
        crop = cv2.resize(src=crop, dsize=(dwidth, int(height)), interpolation=cv2.INTER_CUBIC)
        return crop


if __name__ == "__main__":
    idfind = Findidcard()
    path = r'E:/myvue/IDcard_recog/idcardocr_system_back/idcard_ocr/testimages/rotate0.jpg'
    result = idfind.find(path)
    cv2.imshow('res', result)
    cv2.waitKey()
