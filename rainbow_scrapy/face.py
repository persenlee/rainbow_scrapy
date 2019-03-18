from aip import AipFace
import json

APP_ID = '15721234'
API_KEY = 'KbNFdcZmxUFCW1dHxe024C3u'
SECRET_KEY = 'YTUsx9UpiyXomuhg3331j8wAWsbYObP7'


class FaceDetector(object):
    client = AipFace(APP_ID, API_KEY, SECRET_KEY)
    @staticmethod
    def is_human_in_image(image_url):
        image_type = 'URL'
        options = dict()
        options['max_face_num'] = 2
        options["face_field"] = "quality,gender,face_type"
        dic = FaceDetector.client.detect(image_url, image_type, options)
        result = dic.get('result', None)
        if result is None:
            return False
        else:
            face_num = result['face_num']  # 脸的数量

            face_list = result['face_list']
            for face_info in face_list:
                gender_dic = face_info.get('gender', None)
                is_male = False
                if gender_dic is not None:
                    gender = gender_dic.get('type', None)  # 性别
                    gender_probability = gender_dic.get('probability', None)  # 性别可信度
                    is_male = gender == 'male' and gender_probability > 0.8
                if not is_male:
                    continue

                face_type_dic = face_info.get('face_type', None) # 脸的类型
                is_real_man = False
                if face_type_dic is not None:
                    face_type = face_type_dic['type']  # human: 真实人脸 cartoon: 卡通人脸
                    human_probability = face_type_dic['probability']
                    is_real_man = face_type == 'human' and human_probability > 0.7

                if not is_real_man:
                    continue

                qualities = face_info.get('quality', None)  # 人脸质量信息
                is_quality_pass = False
                if qualities is not None:
                    occlusion = qualities['occlusion']  # 遮挡范围
                    left_check = occlusion['left_cheek']  # 左脸颊被遮挡的阈值
                    right_check = occlusion['right_cheek']  # 右脸颊被遮挡的阈值
                    blur = qualities['blur']  # 模糊度范围
                    illumination = qualities['illumination']  # 光照范围
                    completeness = qualities['completeness']  # 人脸完整度
                    occlusion_quality = left_check * right_check  # 左右脸遮挡面积比例
                    is_quality_pass = completeness > 0.4 and illumination > 20 and blur < 0.5 and occlusion_quality < 0.36

                is_good_image = (face_num > 0 and is_quality_pass and is_real_man and is_male)
                if is_good_image:
                    return True
        return False
