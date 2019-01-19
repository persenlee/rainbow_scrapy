import scrapy
from urllib.parse import quote
import json
from rainbow_scrapy.items import ImageItem

class BingImageSpider(scrapy.Spider):
    name = 'BingImageSpider'
    def start_requests(self):
        data = {'queryWord': 'site:aipxtk.net','pageNum': 35}
        base_url_template = 'https://cn.bing.com/images/async?q={0}&first={1}&count={2}&relp={3}&scenario=ImageBasicHover&datsrc=N_I&layout=RowBased&mmasync=1&dgState=x*685_y*1103_h*207_c*4_i*36_r*6&IG=D75FA50BB1D94E5CBBC6089C9C1EA4FF&SFX=2&iid=images.5594'
        data['first'] = 1
        for page in range(1, 10):
            url = base_url_template.format(quote(data['queryWord']), data['first'], data['pageNum'], data['pageNum'])
            data['first'] += data['pageNum']
            yield scrapy.Request(url, self.parse)

    def parse(self, response):
        ms = response.xpath('//a[@class="iusc"]/@m').extract()
        for m in ms:
            dic = json.loads(m)
            item = ImageItem()
            item['thumb_src'] = dic['turl']
            item['src'] = dic['murl']
            item['title'] = dic['t']
            yield item