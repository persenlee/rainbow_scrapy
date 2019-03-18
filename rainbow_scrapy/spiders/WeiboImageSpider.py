import scrapy
import json
from rainbow_scrapy.items import ImageItem
import pymysql


class WeiboImageSpider(scrapy.Spider):
    name = 'WeiboImageSpider'
    # 照片墙api
    gallery_url = 'https://m.weibo.cn/api/container/getSecond?containerid=107803{uid}_-_photoall&page={page}&count={count}'
    login_url = 'https://passport.weibo.cn/sso/login'
    connect = None

    def start_requests(self):
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded',
            'Referer': 'https://passport.weibo.cn/signin/login?entry=mweibo&res=wel&wm=3349&r=https%3A%2F%2Fm.weibo.cn%2F'
        }
        body = {
            'username': 'polocoke@163.com',
            'password': '199020092011lpx',
        }
        yield scrapy.FormRequest(url=self.login_url,
                                 method='POST',
                                 meta={'cookiejar': 1},
                                 callback=self.after_login,
                                 headers=headers,
                                 formdata=body, )

    def after_login(self, response):
        self.connect = pymysql.connect(
            host=self.settings.get('MYSQL_HOST'),
            port=self.settings.get('MYSQL_PORT'),
            db=self.settings.get('SCRAPY_DBNAME'),
            user=self.settings.get('MYSQL_USER_NAME'),
            passwd=self.settings.get('MYSQL_USER_PASSWORD'),
            charset='utf8',
            use_unicode=True
        )
        self.connect.autocommit(True)
        cursor = self.connect.cursor()
        sql_text = 'select * from weibo_user'
        cursor.execute(sql_text)
        users = cursor.fetchall()
        for user in users:
            uid = user[0]
            url = self.gallery_url.format(uid=uid, page=1, count=20)
            yield scrapy.Request(url, self.parse, meta={'cookiejar': response.meta['cookiejar'],
                                                        'uid': uid,
                                                        'page': 1})
            # request.meta['uid'] = uid
            # request.meta['page'] = 1
            # yield request


    last_uid = None


    def parse(self, response):
        cards = (json.loads(response.body)['data'])['cards']
        uid = response.meta['uid']
        should_update_user = uid != self.last_uid
        self.last_uid = uid
        for card in cards:
            pics = card['pics']
            for pic in pics:
                item = ImageItem()
                item['thumb_src'] = pic['pic_small']
                item['src'] = pic['pic_big']
                mblog = pic['mblog']
                text = mblog['text']
                if len(text) > 128:
                    text = text[0:128]
                item['title'] = text

                if (should_update_user):
                    weibo_id = mblog['id']
                    self.update_user(uid, weibo_id)
                should_update_user = False

                yield item
        # 分页继续请求
        if (len(cards) > 0):
            page = response.meta['page'] + 1
            url = self.gallery_url.format(uid=uid, page=page, count=20)
            request = scrapy.Request(url, self.parse, meta={'cookiejar': response.meta['cookiejar']}, )
            request.meta['uid'] = uid
            request.meta['page'] = page
            yield request


    def update_user(self, user_id, weibo_id):
        cursor = self.connect.cursor()
        sql_text = 'update weibo_user set last_weibo_id={weibo_id} where id={user_id}'.format(weibo_id=weibo_id,
                                                                                              user_id=user_id)
        result = cursor.execute(sql_text)
        if result == 1:
            print(sql_text + '\n Success!!!')
        else:
            print(sql_text + '\n Failed!!!')
