from dotenv import load_dotenv
import os
import sys
import json
import threading

from src.ProxyHandler import ProxyHandler
from src.Utils import createLogger
from src.Database import Database
from src.Socket import Socket

PROXY_TYPES = []

class Server:

    def __init__(self):

        self.logger = createLogger(
            __name__, 
            "/var/log/{0}/".format(os.getenv('APP_NAME'))
        )
        self.db = Database()

        self.logger.debug("Server:__init__():: {STARTED}")

    def main(self) -> None:
        self.logger.debug("Server:main():: {STARTED}")
        proxyHandlers = {}
        try:
            proxy_urls = {}
            with open('./urls.json', 'r') as file:
                proxy_urls = json.load(file)
            
            threads = []
            for proxy_type in proxy_urls.keys():
                if proxy_type.lower() not in PROXY_TYPES:
                    continue
                try:
                    _proxy = ProxyHandler(self.db, proxy_type, proxy_urls[proxy_type])
                    _thread = threading.Thread(target=_proxy.fetch)
                    _thread.start()
                    threads.append(_thread)
                    proxyHandlers[proxy_type] = _proxy
                except Exception as ex:
                    self.logger.error("Server:main():: {0}".format(ex), exc_info=True)

            for thread in threads:
                thread.join()
        except Exception as ex:
            self.logger.error("Server:main():: {0}".format(ex), exc_info=True)
            sys.exit(-1)

        self.__serve(proxyHandlers)

    def __serve(self, proxyHandlers: dict[str, ProxyHandler]):
        self.logger.debug("Server:__serve():: {STARTED}")
        try:
            for proxyHandler in proxyHandlers.values():
                Socket(proxyHandler)
        except Exception as ex:
            self.logger.error("Server:__serve():: {0}".format(ex), exc_info=True)
            sys.exit(-1)

if __name__ == '__main__':
    load_dotenv()

    PROXY_TYPES = os.environ.get('PROXY_TYPES', '').split(',')
    
    Server().main()
