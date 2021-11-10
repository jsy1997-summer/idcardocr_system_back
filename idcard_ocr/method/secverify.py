import base64
import json
import re

from django.http import response, HttpResponse

from idcard_ocr.method import findidcard, idcardocr


from pyocr.libtesseract import tesseract_raw

firline_text = ""


class Secverify:
    def __init__(self):
        pass

    # 身份证号码校验码验证
    @staticmethod
    def id_verify(idnum):
        # 7－9－10－5－8－4－2－1－6－3－7－9－10－5－8－4－2。
        idsum = int(idnum[0]) * 7 + int(idnum[1]) * 9 + int(idnum[2]) * 10 + int(idnum[3]) * 5 + int(
            idnum[4]) * 8 + int(idnum[5]) * 4 + int(idnum[6]) * 2 + int(idnum[7]) * 1 + int(idnum[8]) * 6 + int(
            idnum[9]) * 3 + int(idnum[10]) * 7 + int(idnum[11]) * 9 + int(idnum[12]) * 10 + int(idnum[13]) * 5 + int(
            idnum[14]) * 8 + int(idnum[15]) * 4 + int(idnum[16]) * 2
        idsum = idsum % 11
        check_code = [1, 0, 'X', 9, 8, 7, 6, 5, 4, 3, 2]
        code = check_code[idsum]
        code = str(code)

        if code == idnum[17]:
            tip = "true"
        else:
            tip = "false"
        print("身份证真伪验证为：" + tip)
        return tip

    # 住址栏首行是11个字验证
    @staticmethod
    def word11_verify():
        # 正则匹配地址里面含有的数字，返回一个包含所有匹配到的数字串的数组
        numarr = re.findall(r'\d+', firline_text)
        num = 0
        # 身份证一个数字35实际上算是一个字，计算多计算出来的数字个数
        for i in range(len(numarr)):
            num = num + len(numarr[i]) - 1
        leng = len(firline_text) - num
        if leng == 11:
            tip = "true"
        else:
            tip = "false"
        print("居住地址首行11字检验为：" + tip)
        return tip

    # 身份证头像照片左侧与下方身份证号码年份最后一个数字中间对齐
    @staticmethod
    def vertical_verify(img):
        ver = idcardocr.Verify()
        tip = ver.vertical_verify(img)
        print("垂直检验为："+tip)
        return tip


def verify(request):
    if request.method == "OPTIONS":
        response.status_code = 200
        return HttpResponse("200")
    if request.method == "POST":
        body = request.body
        body = json.loads(body)
        img = body.get("img_base64")
        card_info = body.get("card_info")

        img = img.split(",")[1]
        img = base64.b64decode(img)
        file = open('E:/myvue/IDcard_recog/idcardocr_system_back/idcard_ocr/testimages/change.jpg', "wb")
        file.write(img)
        file.close()
        imagepath = "E:/myvue/IDcard_recog/idcardocr_system_back/idcard_ocr/testimages/change.jpg"

        idfind = findidcard.Findidcard()
        idcard_img = idfind.find(imagepath)  # 对图像进行校正处理

        handle = tesseract_raw.init(lang='chi_sim')
        handle_num = tesseract_raw.init(lang='eng')
        result_dict = idcardocr.idcardocr(idcard_img, handle, handle_num, 1)
        result_dict['error'] = 0

        idnumber = result_dict["idnum"]
        sec = Secverify()
        verify_res = "验证未通过"
        if sec.id_verify(idnumber) == "true":
            if sec.word11_verify() == "true":
                if sec.vertical_verify(idcard_img) == "true":
                    verify_res = "验证通过"

        result = {
            "card_info": card_info,
            "verify_res": verify_res
        }

        return HttpResponse(json.dumps(result, ensure_ascii=False), content_type="text/html,charset=utf-8")


if __name__ == "__main__":
    ve = Secverify()
    res = ve.word11_verify()
    print(res)
