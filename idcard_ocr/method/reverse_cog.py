# -*-coding:utf-8-*-
import cv2


class Reverse_recognize:
    def __init__(self):
        pass

    def find(self, image):
        print("进入身份证背面匹配流程")
        img = cv2.UMat(cv2.imread(image, 0))
        self.showing(img, "img")
        return 1

    @staticmethod
    def showing(img, name):
        cv2.namedWindow(name, 0)
        cv2.resizeWindow(name, 1280, 720)
        cv2.imshow(name, img)
        cv2.waitKey(0)  # 等待键盘按键


if __name__ == "__name__":
    print("1555")
    path = r"../testimages/jsy_reverse.jpg"
    recog = Reverse_recognize.find(path)
