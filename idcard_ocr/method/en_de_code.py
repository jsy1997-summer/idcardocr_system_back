import json
import random

from Cryptodome.PublicKey import RSA
from Cryptodome.Cipher import PKCS1_v1_5
from django.http import HttpResponse, response
from urllib import parse
import base64

text = "浪费时间是我情愿,像谢幕的演员，眼看着灯光熄灭"
text = text.encode('utf-8')


# 加载公钥和私钥
def get_key(request):
    if request.method == "OPTIONS":
        response.status_code = 200
        return HttpResponse("200")
    if request.method == "POST":
        key = RSA.generate(2048)
        # 得到公钥

        public_key = key.publickey().exportKey()
        # with open("my_rsa_public.pem", "wb") as f:
        #     f.write(public_key)
        with open("rsa_public.pem", "wb") as f:
            f.write(public_key)

        # 得到私钥
        encrypted_key = key.exportKey(pkcs=8, protection="scryptAndAES128-CBC")
        with open("rsa_private_key.bin", "wb") as f:
            f.write(encrypted_key)
        key_data = {
            "public_key": str(public_key),
            "private_key": str(encrypted_key),
        }
        return HttpResponse(json.dumps(key_data, ensure_ascii=False), content_type="text/html,charset=utf-8")
        # return HttpResponse(key_data)

        # json.dumps 序列化时对中文默认使用的ascii编码, 想输出真正的中文需要指定ensure_ascii=False：


# RSA加密
def encode(rsa_data):
    recipient_key = RSA.import_key(
        open("rsa_public.pem").read()
    )
    pubkey = PKCS1_v1_5.new(recipient_key)
    endata = pubkey.encrypt(rsa_data)
    return endata


# RSA解密
def decode(en_data):
    en_data =  (en_data)
    en_data = base64.b64decode(en_data)
    private_key = RSA.import_key(open("rsa_private_key.bin").read())
    prikey = PKCS1_v1_5.new(private_key)
    dataa = prikey.decrypt(en_data, None)
    dataa = dataa.decode('utf-8')  # 有文字的要经过这个转换

    return dataa


# Miser解密
def miser_decode(at, bt, endata):
    a = min(at, bt)  # 选择a为较小的数
    b = max(at, bt)  # 选择b为较大的数值
    # 加密部分截取出来 688为加密部分的密文的长度
    cip = endata[a:a + 688]
    print(a)
    print(b)


    # 还原密文的原来的顺序
    cip = cip[0:b - a] + cip[-(a + b):-1] + cip[-1] + cip[b - a:-(a + b)]
    # cip1l = 0.5 * len(cip)=344 固定长度
    fir_sep = cip[0:344]
    sec_sep = cip[344:]
    # 两个序列进行解密
    fir_sep = decode(fir_sep)
    sec_sep = decode(sec_sep)

    # 根据第一序列和第二序列在整个明文中起始位置的不同选择不同的叠加方法
    if at > bt:
        dedata = endata[0:a] + sec_sep[0:b - a] + fir_sep + endata[a + 688:]
    else:
        dedata = endata[0:a] + fir_sep[0:b - a] + sec_sep + endata[a + 688:]

    return dedata


# Miser加密算法
# 外部对称加密（分段切割加密），内部非对称加密（ras加密）
# Miser 加密
def miser_encode(res_data):
    res_data = str(res_data)
    fir = random.randint(0, 30)  # 第一个序列的起始位置
    sec = random.randint(fir, 30)  # 第二个序列的起始位置
    fir_seq = res_data[fir:fir + 50]  # 截取长度为50的明文串为第一个序列
    sec_seq = res_data[sec:sec + 50]  # 截取长度为50的明文串为第二个序列
    res1 = json.dumps(fir_seq)  # 转换为json格式，
    res1 = bytes(res1, encoding="utf8")  # 转换为bytes格式，否则encode无法接受
    res2 = json.dumps(sec_seq)
    res2 = bytes(res2, encoding="utf8")
    fir_cip = encode(res1)  # 生成第一段序列的密文256
    sec_cip = encode(res2)  # 生成第二段序列的密文256
    fir_cip = base64.b64encode(fir_cip)  # 长度344
    sec_cip = base64.b64encode(sec_cip)
    cip_all = fir_cip + sec_cip
    cip_all = cip_all[0:sec - fir] + cip_all[2 * sec:] + cip_all[sec - fir:2 * sec]  # 打乱密文
    res_all = res_data[0:fir] + str(cip_all) + res_data[sec + 50:]
    return fir, sec, res_all


if __name__ == '__main__':
    # get_key()
    # miser解密测试
    # a1 = 8
    # b1 = 3
    # endata1 = "世界能GDplp+FloQyG65s50zLvygh4G8N4cYIxphCTYyAIYtcPB1C/Xl7mjJ7oarg0PUw8gtXVgs1Uqy7hctcNoU6orV3fe3N95Y4ILtsmCzcaAfOwp+xm9mI5zgaqBAd00I1CGKVsZ1fLpTtrssOgEEa9wyaQTVPbbGHE9n1qpBGA8aTECAO0vn0k5LMooasoCoUpAw55mHb1s14eX1pZcxk3lgW9aFgypvkKzLoqz1FjPjk9WJ4GVufGjNuDnV8iRqbpm1TszoyLQCxL9EbR7drS57QaTZW21eql3QIDZnibyYm/yaSEjKLKb+NpUFJQiZV9Il8eRTweApw==Z3BF5RDVlaIuA8i5g6seBrPwG/omMUVWydJYxLakAMHKn6QKfx7HsEiJhCJRyTrqkrIB/cADMCbPy8NcQgAEuV4SThZeqgIMCVYfQK0KWn/+mbruix6+rnKlApCgMAmhSLJaSfmDCKoxMaXmcdbvnzUG9f+YgvjvEuqUQ/9exoU0tMZV7Pc6JRnSoBXCO+51gNfwbJPV0zxrgFtatUgv/3xAbaR54tXFzq2oUbftOjqiUntQG7IXZbDLVL1eKXqHDbEAZcak90//fxrVdHSKXDwho/vgYyyjTFQv8R/Y6kP0OiPaITWB/BEq3kl+TcoHlRRMXnGJabP/WwAifMp9Hg==t7xmRiQZ1dz无关，人间毫无留恋，一切散为烟"
    # data = miser_decode(a1, b1, endata1)
    # print(data)
    # miser加密测试
    resdata = {'name': '李白', 'sex': '男', 'idnum': '142822197603200075', 'birth': '19760320', 'nation': '汉', 'address': '四川省成都市青羊区二环高架路', 'error': 0}

    dataq = miser_encode(resdata)
    print(dataq)
