import requests
import json
from scrapy.utils.project import get_project_settings


class Proxy(object):
    proxy_array = []

    @staticmethod
    def base_url():
        settings = get_project_settings()
        return settings.get('IP_PROXY_URL')

    @staticmethod
    def get_proxy():
        if len(Proxy.proxy_array) > 0:
            return Proxy.proxy_array[0]
        else:
            try:
                pool = Proxy.get_proxy_pool()
                Proxy.proxy_array.extend(pool)
                if len(Proxy.proxy_array) > 0:
                    return Proxy.proxy_array[0]
                else:
                    return None
            except IOError:
                return None


    @staticmethod
    def get_random_proxy():
        return requests.get(Proxy.base_url()).content.decode("utf-8")

    @staticmethod
    def delete_proxy(proxy):
        Proxy.proxy_array.remove(proxy)
        requests.get(Proxy.base_url() + "/delete/?proxy={}".format(proxy))

    @staticmethod
    def get_proxy_pool():
        content = requests.get(Proxy.base_url() + "/get_all/").content.decode("utf-8")
        pools = json.loads(content)
        return pools
