import requests
from scrapy.utils.project import get_project_settings


class Proxy(object):
    @staticmethod
    def base_url():
        settings = get_project_settings()
        return settings.get('IP_PROXY_URL')

    @staticmethod
    def get_random_proxy():
        return requests.get(Proxy.base_url() + "/get/").content.decode("utf-8")

    @staticmethod
    def delete_proxy(proxy):
        requests.get(Proxy.base_url() + "/delete/?proxy={}".format(proxy))

    @staticmethod
    def get_proxy_pool():
        return requests.get(Proxy.base_url() + "/get_all/").decode("utf-8")
