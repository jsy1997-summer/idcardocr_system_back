import requests


class BaiduOcr:
    def __init__(self):
        pass

    @staticmethod
    def get_token():
        host = 'https://aip.baidubce.com/oauth/2.0/token?grant_type=client_credentials&client_id' \
               '=LvPLhNdk0Hlezq5gVUbDCGen&client_secret=c2AqcSkGGdyDi1HPTXOZhbPowQFTeOh1'
        response1 = requests.get(host)

        res1 = response1.json()
        token = res1['access_token']
        return token

    def ocr(self, cardimg):
        access_token = self.get_token()  # access_token的有效期为30天，为了避免到期再次获取，每次对比就获取一次
        request_url = "https://aip.baidubce.com/rest/2.0/ocr/v1/idcard"
        request_url = request_url + "?access_token=" + access_token
        headers = {'content-type': 'application/x-www-form-urlencoded'}
        params = {"id_card_side": "front", "image": cardimg}
        response = requests.post(request_url, data=params, headers=headers)
        print(response.json())

    def encrypt_ocr(self, cardimg):
        access_token = self.get_token()  # access_token的有效期为30天，为了避免到期再次获取，每次对比就获取一次
        request_url = "https://aip.baidubce.com/rest/2.0/ocr/v1/idcard_enc"
        request_url = request_url + "?access_token=" + access_token
        headers = {'content-type': 'application/x-www-form-urlencoded'}
        # params = {"id_card_side": "front", "image": cardimg, "enc_aes_key" = enc_aes_key}
        response = requests.post(request_url, data=params, headers=headers)
        print(response.json())

