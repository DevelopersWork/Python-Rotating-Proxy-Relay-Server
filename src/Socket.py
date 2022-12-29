import threading
import socket
import os
import sys

from src.Utils import createLogger
from src.ProxyHandler import ProxyHandler
from src.RequestHandler import RequestHandler

class Socket:

    def __init__(self, proxy_handler: ProxyHandler) -> None:
        self.logger = createLogger(
            proxy_handler.type, 
            "/var/log/{0}/{1}/".format(os.getenv('APP_NAME'), __name__),
            stream=False
        )
        self.proxyHandler = proxy_handler
        
        threading.Thread(target=self.__createSocket).start()

    def __createSocket(self):
        try:
            self.logger.debug("Socket:__createSocket():: {STARTED}")
            port = int(os.getenv("{0}_PORT".format(self.proxyHandler.type.upper())))
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as _socket:
                _socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                _socket.bind(('', port))
                _socket.listen()
                self.logger.info("Socket:__createSocket():: {0}:{1}".format(self.proxyHandler.type.upper(),port))
                while True:
                    try:
                        connection, address = _socket.accept()
                        thread = threading.Thread(target=self.__serve, args=(connection, address,))
                        thread.setDaemon(True)
                        thread.start()
                    except socket.timeout:
                        continue
                    except socket.error as ex:
                        self.logger.warning("Socket:__createSocket():: {0}".format(ex), exc_info=True)
                    except Exception as ex: 
                        self.logger.error("Socket:__createSocket():: {0}".format(ex), exc_info=True)
        except KeyboardInterrupt:
            sys.exit(1)

    def __serve(self, connection: socket.socket, address: socket.AddressInfo) -> None:
        if not connection: return None
        self.logger.info("Socket:__serve({1}):: {0}".format(address, self.proxyHandler.type))
        try:
            RequestHandler(self.proxyHandler, connection, address).start()
        except socket.timeout as ex: 
            self.logger.warning("Socket:__serve():: {0}".format(ex), exc_info=True)
        except Exception as ex:
            self.logger.error("Socket:__serve():: {0}".format(ex), exc_info=True)
        