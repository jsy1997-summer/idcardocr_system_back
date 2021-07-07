# -*- coding: utf-8 -*-
# from numpy import unicode

from idcard_ocr.method import idcardocr
from idcard_ocr.method import findidcard
import json
from http.server import BaseHTTPRequestHandler, HTTPServer
import socketserver
import cv2
from pyocr.libtesseract import tesseract_raw
handle = tesseract_raw.init(lang="chi_sim")
handle_num = tesseract_raw.init(lang="eng")


def process(img_name):
    try:
        idfind = findidcard.Findidcard()
        idcard_img = idfind.find(img_name)  # 对图像进行校正处理

        # showing(idcard_img)
        # result_dict = unit_test.idcardocr(idcard_img,handle,handle_num,1)

        result_dict = idcardocr.idcardocr(idcard_img, handle, handle_num, 1)
        result_dict['error'] = 0
    except Exception as e:
        result_dict = {'error': 1}
        print(e)
    return result_dict


def showing(img):
    cv2.namedWindow("contours", 0)
    # cv2.resizeWindow("contours", 1600, 1200);
    cv2.imshow("contours", img)
    cv2.waitKey()


# SocketServer.ForkingMixIn, SocketServer.ThreadingMixIn
class ForkingServer(socketserver.ThreadingMixIn, HTTPServer):
    pass


class S(BaseHTTPRequestHandler):
    def _set_headers(self):
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        # self.end_headers()

    def do_GET(self):
        self._set_headers()
        # self.wfile.write("<html><body><h1>hi!</h1></body></html>")
        # result = process(pic)

    def do_HEAD(self):
        self._set_headers()

    def do_POST(self):
        content_length = int(self.headers['Content-Length'])  # <--- Gets the size of data
        post_data = self.rfile.read(content_length)  # <--- Gets the data itself
        post_data = post_data.split(b'\r\n')  # 分割信字节流信息
        post_data = post_data[1].split(b';')  # 再次分割
        filename = post_data[2]  # filename信息字节   再转化为str
        filename = bytes.decode(filename)  # 字节流转换为str
        filename = filename[11:-1]  # 得到名字
        pic = "tmp/%s" % filename
        # print(pic)
        result = process(pic)
        # print result
        self._set_headers()
        self.send_header("Content-Length", str(len(json.dumps(result).encode('utf-8'))))
        self.end_headers()
        self.wfile.write(json.dumps(result).encode('utf-8'))
        # 发送消息


def http_server(server_class=ForkingServer, handler_class=S, port=8080):
    server_address = ('', port)
    httpd = server_class(server_address, handler_class)
    cv2.ocl.setUseOpenCL(True)
    print('Starting httpd...')
    print(u"是否启用OpenCL：%s" % cv2.ocl.useOpenCL())
    httpd.serve_forever()


# 作为脚本执行的时候才会被执行，被其他文件import是我时候不会别执行
# 本模块被执行的时候，__name__=="__main__",被其他模块import的时候，__name__=="idcard_recognize"(文件名)
if __name__ == "__main__":
    # http_server()
    process('idcard_ocr/testimages/1.jpg')
