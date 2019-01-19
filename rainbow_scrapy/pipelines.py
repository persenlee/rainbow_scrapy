# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html
from scrapy.pipelines.images import  ImagesPipeline
from scrapy import Request
from scrapy.exceptions import DropItem
import pymysql
import datetime

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
    def __init__(self,settings):
        self.connect = None
        self.cursor = None
        self.settings = settings



    def process_item(self, item, spider):
            dt = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            sqltext = self.insert_sql.format(
                title=pymysql.escape_string(item['title']),
                src=pymysql.escape_string(item['src']),
                create_time=dt,
                thumb_src=pymysql.escape_string(item['thumb_src']))
            # spider.log(sqltext)
            self.cursor.execute(sqltext)

    def open_spider(self,spider):
        self.connect = pymysql.connect(
            host = self.settings.get('MYSQL_HOST'),
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
