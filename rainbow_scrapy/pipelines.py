# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html
from scrapy.pipelines.images import ImagesPipeline
from scrapy import Request
from scrapy.exceptions import DropItem
import pymysql
import datetime
from rainbow_scrapy.items import ImageItem, WeiboUserItem
from rainbow_scrapy.face import FaceDetector
from rainbow_scrapy.spiders import WeiboImageSpider

class RainbowScrapyPipeline(ImagesPipeline):
    def file_path(self, request, response=None, info=None):
        url = request.url
        file_name = url.split('/')[-1]
        return file_name

    def item_completed(self, results, item, info):
        image_paths = [x['path'] for ok, x in results if ok]
        if not image_paths:
            raise DropItem('Image Downloaded Failed')
        return item

    def get_media_requests(self, item, info):
        yield Request(item['src'])


class RainbowDatabasePipeline(object):
    insert_sql = '''insert into image(title,src,create_time,thumb_src,tags)
                            values('{title}','{src}','{create_time}','{thumb_src}','')'''

    def __init__(self, settings):
        self.connect = None
        self.cursor = None
        self.settings = settings

    def process_item(self, item, spider):
        if isinstance(item, ImageItem):
            if spider.name == 'WeiboImageSpider':
                is_human = FaceDetector.is_human_in_image(item['src'])
                if(not is_human):
                    return
            dt = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            sql_text = self.insert_sql.format(
                title=pymysql.escape_string(item['title']),
                src=pymysql.escape_string(item['src']),
                create_time=dt,
                thumb_src=pymysql.escape_string(item['thumb_src']))
            self.cursor.execute(sql_text)

    def open_spider(self, spider):
        self.connect = pymysql.connect(
            host=self.settings.get('MYSQL_HOST'),
            port=self.settings.get('MYSQL_PORT'),
            db=self.settings.get('MYSQL_DBNAME'),
            user=self.settings.get('MYSQL_USER_NAME'),
            passwd=self.settings.get('MYSQL_USER_PASSWORD'),
            charset='utf8',
            use_unicode=True
        )
        self.cursor = self.connect.cursor();
        self.connect.autocommit(True)

    def close_spider(self, spider):
        self.cursor.close()
        self.connect.close()

    @classmethod
    def from_crawler(cls, crawler):
        return cls(crawler.settings)


class WeiboUserPipeline(object):
    insert_sql = '''insert into weibo_user(id,name,followers_count)
                            values('{id}','{name}','{followers_count}')'''

    def __init__(self, settings):
        self.connect = None
        self.cursor = None
        self.settings = settings

    def process_item(self, item, spider):
        if isinstance(item, WeiboUserItem):
            sql_text = self.insert_sql.format(
                id=item['id'],
                name=pymysql.escape_string(item['name']),
                followers_count=item['followers_count'])
            self.cursor.execute(sql_text)
        else:
            return item

    def open_spider(self, spider):
        self.connect = pymysql.connect(
            host=self.settings.get('MYSQL_HOST'),
            port=self.settings.get('MYSQL_PORT'),
            db=self.settings.get('SCRAPY_DBNAME'),
            user=self.settings.get('MYSQL_USER_NAME'),
            passwd=self.settings.get('MYSQL_USER_PASSWORD'),
            charset='utf8',
            use_unicode=True
        )
        self.cursor = self.connect.cursor();
        self.connect.autocommit(True)

    def close_spider(self, spider):
        self.cursor.close()
        self.connect.close()

    @classmethod
    def from_crawler(cls, crawler):
        return cls(crawler.settings)
