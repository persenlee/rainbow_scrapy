import scrapy
import re
from urllib.parse import quote
from rainbow_scrapy.items import ImageItem
import json

class BaiduImageSpider(scrapy.Spider):
    name = "BaiduImageSpider"
    # start_urls = [
    #     'http://quotes.toscrape.com/page/1/',
    # ]

    def start_requests(self):
        data = {'queryWord': '熊猫', 'word': '熊猫'}
        base_url = 'https://image.baidu.com/search/acjson?tn=resultjson_com&ipn=rj&ct=201326592&is=&fp=result&queryWord='
        for page in range(1, 10):
            data['pn'] = page * 30
            url = base_url + quote(data['queryWord']) + '&cl=2&lm=-1&ie=utf-8&oe=utf-8&adpicid=&st=-1&z=&ic=0&word=' + \
                  quote(data['word']) + '&s=&se=&tab=&width=&height=&face=0&istype=2&qc=&nc=1&fr=&expermode=&pn=' + \
                  quote(str(data['pn'])) + '&rn=30&gsm=' + str(hex(data['pn']))
            yield scrapy.Request(url, self.parse)



    def parse(self, response):
        images = json.loads(response.body)['data']
        for image in images:
            item = ImageItem()
            objurl = image.get('objURL')
            srcurl = self.decode_objurl(objurl)
            if srcurl is not None:
                item['src'] = srcurl
            else:
                item['src'] = image.get('middleURL')
            item['title'] = image.get('fromPageTitleEnc');
            item['thumb_src'] = image.get('middleURL')
            yield item


        # next_page = response.css('li.next a::attr(href)').extract_first()
        # if next_page is not None:
        #     yield response.follow(next_page, callback=self.parse)

    def decode_objurl(self,url):
            res = ''
            c = ['_z2C$q', '_z&e3B', 'AzdH3F']
            d = {'w': 'a', 'k': 'b', 'v': 'c', '1': 'd', 'j': 'e', 'u': 'f', '2': 'g', 'i': 'h', 't': 'i', '3': 'j',
                 'h': 'k', 's': 'l', '4': 'm', 'g': 'n', '5': 'o', 'r': 'p', 'q': 'q', '6': 'r', 'f': 's', 'p': 't',
                 '7': 'u', 'e': 'v', 'o': 'w', '8': '1', 'd': '2', 'n': '3', '9': '4', 'c': '5', 'm': '6', '0': '7',
                 'b': '8', 'l': '9', 'a': '0', '_z2C$q': ':', '_z&e3B': '.', 'AzdH3F': '/'}
            if (url == None or 'http' in url):
                return url
            else:
                j = url
                for m in c:
                    j = j.replace(m, d[m])
                for char in j:
                    if re.match('^[a-w\d]+$', char):
                        char = d[char]
                    res = res + char
                return res

