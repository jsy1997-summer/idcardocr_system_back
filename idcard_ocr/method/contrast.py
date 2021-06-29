from imutils import face_utils
import numpy as np
import dlib
import cv2
import base64
from flask import Flask, request, jsonify, json, Response
predictor_path = "D:/model/shape_predictor_68_face_landmarks.dat"
face_rec_model_path = "D:/model/dlib_face_recognition_resnet_model_v1.dat"
shape_predictor = dlib.shape_predictor(predictor_path)
face_rec_model = dlib.face_recognition_model_v1(face_rec_model_path)
detector = dlib.get_frontal_face_detector()
MAR_THRESH = 0.5
EAR_THRESH = 0.21

app = Flask(__name__)
app.config['JSON_SORT_KEYS'] = False

# 提取人脸图片特征点，计算128维向量
def face_duibi(img):
    b, g, r = cv2.split(img)
    img2 = cv2.merge([r, g, b])
    # 检测人脸
    faces = detector(img, 0)
    if len(faces):
        for index, face in enumerate(faces):
            # # 提取68个特征点
            shape = shape_predictor(img2, face)
            # 计算人脸的128维的向量
            face_descriptor = face_rec_model.compute_face_descriptor(img2, shape)
            return face_descriptor
    else:
        pass

# 将计算好的人脸128维向量放入数组中
def face_duibi2(face_descriptor1, face_descriptor2, face_descriptor3):
    dist = []
    dist.append(list(face_descriptor1))
    dist.append(list(face_descriptor2))
    dist.append(list(face_descriptor3))
    return dist

# 计算两个人脸图片向量的欧氏距离
def dist_o(dist_1, dist_2):
    dis = np.sqrt(sum((np.array(dist_1) - np.array(dist_2)) ** 2))
    return dis

# 判断是否是同一个人
def score(img_1, img_2, img_3):
    data = face_duibi2(face_duibi(img_1), face_duibi(img_2), face_duibi(img_3))
    goal1 = dist_o(data[0], data[1])
    goal2 = dist_o(data[1], data[2])
    goal3 = dist_o(data[0], data[2])
    if(goal1 < 0.6 and goal2 < 0.6 and goal3 < 0.6):
        return True
    else: return False
    # 判断结果，如果goal小于0.6的话是同一个人，否则不是。我所用的是欧式距离判别

# 对base64进行解码得到cv可以处理的图片
def base64_to_image(base64_code):
    # base64解码
    img_data = base64.b64decode(base64_code)
    # 转换为np数组
    img_array = np.fromstring(img_data, np.uint8)
    # 转换成opencv可用格式
    img = cv2.imdecode(img_array, cv2.COLOR_RGB2BGR)
    return img

# 图片进行base64编码
def image_to_base64(image_np):
    image = cv2.imencode('.jpg', image_np)[1]
    image_code = str(base64.b64encode(image))[2:-1]
    return image_code

# 文件流转换为cv可以处理的图片
def file_to_image(img):
    fileNPArray = np.frombuffer(img, np.uint8)
    img = cv2.imdecode(fileNPArray, cv2.IMREAD_COLOR)
    return img

def eye_aspect_ratio(eye):
    A = np.linalg.norm(eye[1] - eye[5])
    B = np.linalg.norm(eye[2] - eye[4])
    C = np.linalg.norm(eye[0] - eye[3])
    ear = (A + B) / (2.0 * C)

    return ear

def mouth_aspect_ratio(mouth):
    A = np.linalg.norm(mouth[2] - mouth[9])  # 51, 59
    B = np.linalg.norm(mouth[4] - mouth[7])  # 53, 57
    C = np.linalg.norm(mouth[0] - mouth[6])  # 49, 55
    mar = (A + B) / (2.0 * C)

    return mar

# 对图片进行灰度处理以及定位，返回定位后的特征点
def gray(img):
    # print("[INFO] loading facial landmark predictor...")
    # frame = cv2.imread(img)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    rects = detector(gray, 0)

    if len(rects) == 1:
        rect = rects[0]
        shape = shape_predictor(gray, rect)
        shape = face_utils.shape_to_np(shape)
        return shape
    else:
        return "many people"

# 判断是否闭眼，计算眼睛宽长比，返回比值
def blink_detection(shape):
    # grab the indexes of the facial landmarks for the left and
    # right eye, respectively
    (lStart, lEnd) = face_utils.FACIAL_LANDMARKS_IDXS["left_eye"]
    (rStart, rEnd) = face_utils.FACIAL_LANDMARKS_IDXS["right_eye"]

    left_eye = shape[lStart:lEnd]
    right_eye = shape[rStart:rEnd]
    left_ear = eye_aspect_ratio(left_eye)
    right_ear = eye_aspect_ratio(right_eye)
    ear = (left_ear + right_ear) / 2.0

    return ear

# 判断是否张嘴，判断嘴巴宽长比，返回比值
def mouth_detection(shape):
    (mStart, mEnd) = face_utils.FACIAL_LANDMARKS_IDXS["mouth"]

    mouth = shape[mStart:mEnd]
    mar = mouth_aspect_ratio(mouth)

    # check to see if the eye aspect ratio is below the blink
    # threshold, and if so, increment the blink frame counter
    return mar

# 请求参数为文件流时
@app.route('/predict', methods=['POST', 'GET'])
def predict():
    if request.method == 'POST':
        img_1 = file_to_image(request.files['img1'].stream.read())
        img_2 = file_to_image(request.files['img2'].stream.read())
        img_3 = file_to_image(request.files['img3'].stream.read())
        if (score(img_1, img_2, img_3)):
            shape1 = gray(img_1)
            shape2 = gray(img_2)
            shape3 = gray(img_3)
            ear1 = blink_detection(shape1)
            mar1 = mouth_detection(shape1)
            ear2 = blink_detection(shape2)
            mar2 = mouth_detection(shape2)
            ear3 = blink_detection(shape3)
            mar3 = mouth_detection(shape3)
            if (ear1 < 0.2 or ear2 < 0.2 or ear3 < 0.2 or mar1 > 0.6 or mar2 > 0.6 or mar3 > 0.6):
                return "是活体"
            else:
                return "不是活体"
        else:
            return "不是同一个人"
    elif request.method == 'GET':
        img_1 = 'D:/faces/blink.jpg'
        img1 = cv2.imread(img_1,)
        imgbase = image_to_base64(img1)
        return str(imgbase)

# 请求参数为base64编码时
@app.route('/base64test', methods=['POST', 'GET'])
def base64test():
    if request.method == 'POST':
        img_data = request.get_json()
        img = []
        shape = []
        ear = []
        mar = []

        for i in range(3):
            if img_data[i]["image_type"] == "BASE64":
                img.append(base64_to_image(img_data[i]["image"]))

         #判断是否是同一个人，
        if score(img[0], img[1], img[2]):
            for i in range(3):
                shape.append(gray(img[i]))
                ear.append(blink_detection(shape[i]))
                mar.append(mouth_detection(shape[i]))
        else: return "bushiyigeren"

        face_list = [
            {
                'face_token': '1',
                'mouth': mar[0],
                'eye': ear[0]
            },
            {
                'face_token': '2',
                'mouth': mar[1],
                'eye': ear[1]
            },
            {
                'face_token': '3',
                'mouth': mar[2],
                'eye': ear[2]
            }
        ]

        if (ear[0] < EAR_THRESH or ear[1] < EAR_THRESH or ear[2] < EAR_THRESH or mar[0] > MAR_THRESH or mar[1] > MAR_THRESH or mar[2] > MAR_THRESH):
            result = { 'liveness': True,
                       'face_list':face_list
                       }
        else:
            result = {'liveness': False,
                      'face_list': face_list
                      }
        return  Response(json.dumps(result), mimetype='application/json')

if __name__ == '__main__':
    app.run()

