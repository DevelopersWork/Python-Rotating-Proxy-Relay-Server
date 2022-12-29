import socket
import os

from src.Utils import createLogger
from src.Database import Database

socket.setdefaulttimeout(int(os.getenv('CONNECTION_TIMEOUT')))

class Proxy:

    def __init__(self, ip: str, port: int, type:str, database: Database) -> None:
        self.logger = createLogger(
            "{0}:{1}".format(ip, port), 
            "/var/log/{0}/{1}/".format(os.getenv('APP_NAME'), __name__),
            stream = False
        )

        self.db = database

        self.connection = None
        self.address = ip
        self.port = port
        self.type = type
        self.connected = False
        self.__query = "ip='{0}' and port='{1}' and type='{2}'".format(self.address, self.port, self.type)

        self.alive = self.__is_alive()

    def toggleAvailable(self, available: int) -> bool:
        return self.db.update("proxies", "available='{0}'".format(available), self.__query)
    def setAlive(self, alive: int) -> bool:
        return self.db.update("proxies", "alive='{0}'".format(alive), self.__query)

    def __is_alive(self, _recursiveDepth = 0, type = '') -> bool:
        if _recursiveDepth == int(os.getenv('PROXY_RETRIES')):
            self.logger.warn("Proxy:__is_alive({1}:{2}):: {0}".format(ex, self.address, self.port), exc_info=True)
            return False

        try:
            if type == '':
                self.connection = socket.create_connection((self.address, int(self.port)))
            elif type == 'UDP':
                self.connection = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
                self.connection.connect((self.address, int(self.port)))
            elif type == 'TCP':
                self.connection = socket.socket(family=socket.AF_INET, type=socket.SOCK_STREAM)
                self.connection.connect((self.address, int(self.port)))
            else:
                return False

            self.connected = True
        except socket.timeout as ex:
            if not self.connected and self.connection:
                self.connection.close()
            if _recursiveDepth < int(os.getenv('PROXY_RETRIES')) // 2:
                return self.__is_alive(_recursiveDepth + 1, 'TCP')
            else:
                return self.__is_alive(_recursiveDepth + 1, 'UDP')
        except Exception as ex:
            self.logger.error("Proxy:__is_alive({1}:{2}):: {0}".format(ex, self.address, self.port), exc_info=True)
        finally:
            if self.connected:
                return self.setAlive(1)
        
        self.setAlive(0)
        return False