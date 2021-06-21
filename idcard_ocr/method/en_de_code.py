import json

from Cryptodome.PublicKey import RSA
from Cryptodome.Cipher import PKCS1_OAEP, PKCS1_v1_5
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
        with open("my_rsa_public.pem", "wb") as f:
            f.write(public_key)

        # 得到私钥
        encrypted_key = key.exportKey(pkcs=8, protection="scryptAndAES128-CBC")
        with open("my_private_rsa_key.bin", "wb") as f:
            f.write(encrypted_key)
        key_data = {
            "public_key": str(public_key),
            "private_key": str(encrypted_key),
        }
        return HttpResponse(json.dumps(key_data, ensure_ascii=False), content_type="text/html,charset=utf-8")
        # return HttpResponse(key_data)

        # json.dumps 序列化时对中文默认使用的ascii编码, 想输出真正的中文需要指定ensure_ascii=False：


# RSA加密
def encode(data):
    recipient_key = RSA.import_key(
        open("my_rsa_public.pem").read()
    )
    pubkey = PKCS1_v1_5.new(recipient_key)
    endata = pubkey.encrypt(data)
    return endata


# RSA解密
def decode(en_data):
    en_data = parse.unquote(en_data)
    en_data = base64.b64decode(en_data)
    private_key = RSA.import_key(open("my_private_rsa_key.bin").read())
    prikey = PKCS1_v1_5.new(private_key)
    data = prikey.decrypt(en_data, "解密失败")
    data = data.decode('utf-8')  # 有文字的要经过这个转换
    return data


# Miser加密算法
# 外部对称加密（分段切割加密），内部非对称加密（ras加密）

# Miser解密
def miser_decode(a, b, len_cip, endata):
    a = min(a, b)  # 选择a为较小的数
    b = max(a, b)  # 选择b为较大的数值
    # 加密部分截取出来
    cip = endata[a:a + len_cip]
    # 还原密文的原来的顺序
    cip = cip[0:b - a] + cip[-(a + b):-1] + cip[b - a:-(a + b)]
    cip1l = 0.5 * len(cip)
    fir_sep = cip[0:cip1l]
    sec_sep = cip[cip1l:-1]
    # 两个序列进行解密
    fir_sep = decode(fir_sep)
    sec_sep = decode(sec_sep)
    dedata = endata[0:a] + fir_sep[0:b - a] + sec_sep + endata[a + len_cip:-1]
    return dedata


if __name__ == '__main__':
    # get_key()
    a1 = 12
    b1 = 9
    clength = 688
    # with open('data.txt', 'r') as f:
    #     endata1 = f.read()
    endata1 = '如果我是一朵花，我qYubUtW/qR1Q7bmKU0MhNTofU2OD56fvKJpLn6Hm6E7Yhi6/71ul3Oh1Y5x+47t3I7zLmsKUycqf6/BpKJ7M6AVnEeopHX6/kr6TatkH1efTSQqsdHGRQbSgOwKGrKHvdmhT+NlsMylbj8oRdOui2JFD/s/WYj7zZBKpODX52jMV7T7cMWdtslLg0DAe5YNRQ60Cc7FU8SqGgsOmMD0SLoA+hsdHuGsUWl+4hWVUNhWBKG/4uqAFmSr8v94CShbtpLf3o3RW5a/DltEeFS87InE6Usdmz+IFMoBELPHHHpEd5lSGMSZLeuNa04SFYZuNA==F1HrG/q39ht/w78GC3w9az7RXIHNPBxoc9q3oiPbnXu+7u0ypxL8NJFsxLAw0PppOvfNmmNVff5CR5nE68yUFO+kNLrKRdI/hG9DVzTT/LqBUFgyiGjsbf+lIwR/Mx/tVmhAsVvqkjj62kjk6G6JvqEfzUYmthFJ0lpe6eBj4+ZwzPTPbxJXkPojtpwDOMR2FR1816EO6SahPyLuEqDqBooFOFsgjGWBHpnL5E9walf+YJKFjENeGvSbxE1brIALpMzbk/I500u89/E+rG5nu2y5h2n6uZF4sooHioGkIhuPXTH/lS6GaEU4TgpOOp5AyhRqc0C0lYJ45d33JXCqrg==GxY5K9OFyB6bLnS77iMOF生命，出现了奇迹，而担心'
    data = miser_decode(a1, b1, clength, endata1)
    print(data)
