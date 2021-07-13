import json

from django.http import response, HttpResponse

from manage import CardRecognition


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
            tip = "验证通过"
        else:
            tip = "验证未通过"
        return tip


def verify(request):
    if request.method == "OPTIONS":
        response.status_code = 200
        return HttpResponse("200")
    if request.method == "POST":
        body = request.body
        body = json.loads(body)
        img = body.get("img_base64")
        eg1 = CardRecognition()
        resu = eg1.nocode_reg(img)
        idnumber = resu["idnum"]
        sec = Secverify()
        result = sec.id_verify(idnumber)
        return HttpResponse(result)


if __name__ == "__main__":
    ve = Secverify()
    idnum1 = "142622199411240043"
    res = ve.id_verify(idnum1)
    print(res)
