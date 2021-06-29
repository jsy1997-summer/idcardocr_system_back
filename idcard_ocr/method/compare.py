# -*- coding: utf-8 -*-
"""
Created on Tue Mar 30 17:24:13 2021

@author: dell
"""

# -*- encoding=utf-8 -*-

import cv2
import matplotlib.pyplot as plt
import time


# 自定义计算两个图片相似度函数
def similarity(img1_path, img2_path):
    """
    :param img1_path: 图片1路径
    :param img2_path: 图片2路径
    :return: 图片相似度
    """
    try:
        # 读取图片 加载灰度图片
        img1 = cv2.imread(img1_path, 0)
        img2 = cv2.imread(img2_path, 0)

        # 初始化ORB检测器
        orb = cv2.ORB_create()  # 设置orb算法的各种默认参数
        kp1, des1 = orb.detectAndCompute(img1, None)  # 计算图像中的特征点kp1和描述子的是
        kp2, des2 = orb.detectAndCompute(img2, None)

        '''
        #初始化surf检测器
        surf = cv2.xfeatures2d.SURF_create()
        kp1, des1 = surf.detectAndCompute(img1,None)
        print("456")
        kp2, des2 = surf.detectAndCompute(img2,None)
        '''
        '''
        #初始化sift检测器
        sift = cv2.xfeatures2d.SIFT_create()
        kp1, des1 = sift.detectAndCompute(img1,None)
        kp2, des2 = sift.detectAndCompute(img2,None)
        '''

        '''
        #特征点提取的图片
        img11=cv2.drawKeypoints(img1,kp1,None,color=(0,255,0),flags=0)
        img22=cv2.drawKeypoints(img2,kp2,None,color=(0,255,0),flags=0)
        plt.subplot(1,2,1)
        plt.imshow(img11)
        plt.subplot(1,2,2)
        plt.imshow(img22)
        '''

        # ORB提取并计算特征点
        bf = cv2.BFMatcher(cv2.NORM_HAMMING)  # 建立匹配关系
        # BFMatcher总是尝试所有匹配，从而使得它总是能够得到最佳匹配
        # flann.knnMatch（Fast Library forApproximate Nearest Neighbors）算法更快但是找到的是最近邻似匹配
        # 需要找到一个相对好的匹配但是不需要最佳匹配的时候往往使用FlannBasedMatcher
        # knn筛选结果
        matches = bf.knnMatch(des1, trainDescriptors=des2, k=3)  # 匹配描述子
        '''
        #描述匹配图，两张图上面的点一一对应
        bf = cv2.BFMatcher(cv2.NORM_HAMMING,crossCheck=True) #建立匹配关系
        matches=bf.match(des1,des2) #匹配描述子
        mathces=sorted(matches,key=lambda x:x.distance) #据距离来排序
        img3 = cv2.drawMatches(img1=img1,
                       keypoints1=kp1,
                       img2=img2,
                       keypoints2=kp2,
                       matches1to2=mathces[:20],
                       outImg = None) #画出匹配关系

        plt.imshow(img3)
        plt.show() 
        '''
        '''
        #sift和surf计算特征点
        FLANN_INDEX_KDTREE = 0
        index_params = dict(algorithm = FLANN_INDEX_KDTREE, trees = 5)
        search_params = dict(checks = 10)

        flann = cv2.FlannBasedMatcher(index_params, search_params)
        matches = flann.knnMatch(des1,des2,k=2)
        '''
        # 查看最大匹配点数目
        good = [m for (m, n) in matches if m.distance < 0.75 * n.distance]
        # print(len(good))
        # print(len(matches))
        similary = len(good) / len(matches)
        print("两张图片相似度为:%s" % similary)
        return similary

    except:
        print('无法计算两张图片相似度')
        return '0'


if __name__ == '__main__':
    t1 = round(time.time() * 1000)
    img1_path = r'testimages/nation.jpg'
    img2_path = r'testimages/nation_mask.jpg'

    # img1_path=r'E:/model/three_model_image/lei.jpg'
    # img1_path=r'E:/model/test/jsy_blink0_mouth1.jpg'
    # img2_path=r'E:/model/test/jsy.jpg'

    similary = similarity(img1_path, img2_path)
    t2 = round(time.time() * 1000)
    print("耗费时间为：%s" % (t2 - t1))
