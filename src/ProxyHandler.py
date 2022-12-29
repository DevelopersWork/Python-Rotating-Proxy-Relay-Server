import requests
import os

from src.Utils import createLogger
from src.Proxy import Proxy
from src.Database import Database

class ProxyHandler:

    def __init__(self, db: Database, proxy_type = 'http', urls = []) -> None:
        self.logger = createLogger(
            proxy_type, 
            "/var/log/{0}/{1}/".format(os.getenv('APP_NAME'), __name__)
        )
        self.logger.debug("ProxyHandler:__init__():: {STARTED}")
        self.type = proxy_type
        self.__urls = urls
        
        self.db = db

    def fetch(self) -> None:
        query = "SELECT count(*) FROM proxies WHERE alive!='0' and type='{0}' LIMIT 1".format(self.type)

        response = self.db.executeQuery(query)
        data = response.fetchone()
        if data and data[0] > 0:
            return self.logger.info("ProxyHandler:fetch():: {0}'s {1} proxies".format(self.type, data[0]))

        self.__fetch()
        response = self.db.executeQuery(query)
        data = response.fetchone()
        if data:
            self.logger.info("ProxyHandler:fetch():: {0}: {1}".format(self.type, data[0]))

    def __fetch(self) -> None:
        self.logger.debug("ProxyHandler:__fetch():: {STARTED}")

        ips = list()
        for url in self.__urls:
            response = requests.get(url)
            if response.status_code != 200:
                continue
            ips += response.text.split("\n")
        ips = set(ips)
    
        self.db.delete("proxies", "type='{0}'".format(self.type))
        values = []
        for ip in ips:
            if not ip or len(ip.split(":")) != 2: 
                continue
            address = ip.split(":")[0]
            port = int(ip.split(":")[1])
            values.append("'{0}', '{1}', '{2}', '-1', '1'".format(address, port, self.type))

        try:
            self.db.insert('proxies', "{0}".format("),(".join(values)))
        except KeyboardInterrupt as ex:
            pass
        except Exception as ex:
            self.logger.error("ProxyHandler:__fetch():: {0}".format(ex), exc_info=True)

        return self.get()

    def get(self, _recursiveDepth = 0) -> Proxy:
        try:
            if _recursiveDepth == int(os.getenv('PROXY_RETRIES')): return None
            query = "SELECT * FROM proxies WHERE alive!='0' and available='1' and type='{0}' LIMIT 1"
            response = self.db.executeQuery(query.format(self.type))
            
            data = response.fetchone()
            if not data: 
                return self.__fetch()

            proxy = Proxy(data[0], int(data[1]), self.type, self.db)
            if proxy.alive:
                proxy.toggleAvailable(0)
                return proxy

        except KeyboardInterrupt as ex:
            pass
        except Exception as ex:
            self.logger.error("ProxyHandler:get():: {0}".format(ex), exc_info=True)
        return self.get(_recursiveDepth + 1)
