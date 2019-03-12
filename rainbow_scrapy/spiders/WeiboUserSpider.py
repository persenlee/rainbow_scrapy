import scrapy
from urllib.parse import quote
import json
from rainbow_scrapy.items import WeiboUserItem


class WeiboUserSpider(scrapy.Spider):
    name = 'WeiboUserSpider'
    follow_url = 'https://m.weibo.cn/api/container/getIndex?containerid=231051_-_followers_-_{uid}&page={page}'

    def start_requests(self):
        user_id = '2471798692'
        profile_url = 'https://m.weibo.cn/profile/info?uid={uid}'
        # 粉丝api
        fan_url = 'https://m.weibo.cn/api/container/getIndex?containerid=231051_-_fans_-_{uid}&page={page}'
        # 关注api
        for page in range(1, 10):
            url = self.follow_url.format(uid=user_id,page=page)
            yield scrapy.Request(url, self.parse)

    def parse(self, response):
        cards = (json.loads(response.body)['data'])['cards']
        card_group = cards[0]['card_group']
        for card in card_group:
            user = card['user']
            followers_count = user['followers_count']
            if followers_count > 1000:
                item = WeiboUserItem()
                item['id'] = user['id']
                # for page in range(1, followers_count / 20):
                #     yield scrapy.Request(self.follow_url.format(uid=item['id'], page=page))
                item['name'] = user.get('screen_name')
                item['followers_count'] = followers_count
            yield item
