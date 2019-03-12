from aip import AipFace
import json

APP_ID = '15721234'
API_KEY = 'KbNFdcZmxUFCW1dHxe024C3u'
SECRET_KEY = 'YTUsx9UpiyXomuhg3331j8wAWsbYObP7'


class FaceDetector(object):
    @staticmethod
    def is_human_in_image(image_url):
        client = AipFace(APP_ID, API_KEY, SECRET_KEY)
        image_type = 'URL'
        options = {'max_face_num': 2}
        dic = client.detect(image_url, image_type, options)
        result = dic.get('result', None)
        if result is None:
            return False
        else:
            face_num = result['face_num']
            return face_num > 0
