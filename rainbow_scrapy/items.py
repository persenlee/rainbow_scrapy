# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy

class ImageItem(scrapy.Item):
    title = scrapy.Field()
    src = scrapy.Field()
    url = scrapy.Field()
    width = scrapy.Field()
    height = scrapy.Field()
    md5 = scrapy.Field()
    tags = scrapy.Field()
    thumb_src = scrapy.Field()
