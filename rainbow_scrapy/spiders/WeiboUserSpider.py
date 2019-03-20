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

        url = self.follow_url.format(uid=user_id, page=1)
        yield scrapy.Request(url, self.parse, meta={'page': 1,'uid' : user_id})

    def parse(self, response):
        cards = (json.loads(response.body)['data'])['cards']
        if len(cards) > 0:
            card_group = cards[0]['card_group']
            for card in card_group:
                user = card.get('user', None)
                if user is None:
                    continue
                followers_count = user['followers_count']
                if 1000 <= followers_count <= 50000:
                    ##如果粉丝数大于3w，并且认证过。大概率不是目标user
                    if followers_count >= 30000:
                        verified = user['verified']
                        if verified:
                            continue
                    item = WeiboUserItem()
                    item['id'] = user['id']
                    item['name'] = user.get('screen_name')
                    item['followers_count'] = followers_count
                    url = self.follow_url.format(uid=user['id'], page=1)
                    yield scrapy.Request(url, self.parse, meta={'page': 1, 'uid': user['id']})
                    yield item

            if len(card_group) > 0:
                page = response.meta['page'] + 1
                user_id = response.meta['uid']
                url = self.follow_url.format(uid=user_id, page=page)
                yield scrapy.Request(url, self.parse, meta={'page': page, 'uid': user_id})
        else:
            print('no more data')

