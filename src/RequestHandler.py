import os
import socks
import socket

socket.setdefaulttimeout(int(os.getenv('CONNECTION_TIMEOUT')))

from src.Proxy import Proxy
from src.ProxyHandler import ProxyHandler
from src.Utils import createLogger

class RequestHandler:

    def __init__(self, proxyHandler: ProxyHandler, client_connection: socket.socket, client_address: socket.AddressInfo) -> None:
        self.logger = createLogger(
            "{1}:{2}_{0}".format(proxyHandler.type, client_address[0],client_address[1]), 
            "/var/log/{0}/{1}/".format(os.getenv('APP_NAME'), __name__),
            stream=False
        )
        self.proxyHandler = proxyHandler
        self.client_connection = client_connection
        self.client_address = client_address

    def __getaddrinfo(self, _request: bytes) -> list[tuple[socket.AddressFamily, socket.SocketKind, int, str, tuple[str, int]]]:
        try:
            properties = {
                'host': 'api.ipify.org',
                'port': 443,
                'family':socket.AF_INET,
                'type': socket.SOCK_STREAM,
                'proto': socket.IPPROTO_TCP
            }
            _url = _request.split('\n')[0].split(' ')[1].split("://")
            if len(_url) > 1:
                _url = _url[1].split("/")[0]
            else:
                _url = _url[0].split("/")[0]

            properties['host'] = _url.split(":")[0]
            port = _url.split(":")
            if len(port) > 1:
                properties['port'] = int(port[1])
            else:
                properties['port'] = 80
            
            if _request.find("Keep-Alive") == -1:
                properties['type'] = socket.SOCK_DGRAM
                properties['proto'] = socket.IPPROTO_UDP
            
            return socket.getaddrinfo(**properties)
        except Exception as ex:
            self.logger.error("RequestHandler:__getaddrinfo():: {0}".format(ex), exc_info=True)

    def __create_connection(self, _request: str) -> socket.socket:
        addrinfo = self.__getaddrinfo(_request.decode('utf-8'))[0]
        print(addrinfo)

        try:
            proxy = self.proxyHandler.get()
            
            connection = socks.socksocket(family=addrinfo[0], type=addrinfo[1])
            connection.set_proxy(socks.HTTP, proxy.address, proxy.port)
            connection.connect(addrinfo[4])
            
            return connection
        except Exception as ex:
            self.logger.error("RequestHandler:__getaddrinfo():: {0}".format(ex), exc_info=True)

        return self.__create_connection(_request)

    def __connect(self) -> socket.socket:
        try:
            _request = self.client_connection.recv(int(os.getenv('BUFFER_SIZE')))
            print(_request)
            connection = self.__create_connection(_request)
            connection.send(_request)
            self.client_connection.send(b'HTTP/1.1 200 CONNECTION ESTABLISHED\r\n\r\n')
            return connection
        except Exception as ex:
            print(ex)
            self.logger.error("RequestHandler:__connect():: {0}".format(ex), exc_info=True)

    def __handshake(self, connection: socket.socket):
        while True:
            try:
                buffer = connection.recv(int(os.getenv('BUFFER_SIZE')))
                print("server", buffer)
                if not buffer: break
                self.client_connection.sendall(buffer)
            except socket.timeout as ex:
                self.logger.warn("RequestHandler:__handshake():: {0}".format(ex), exc_info=True)
            except socket.error as ex:
                self.logger.error("RequestHandler:__handshake():: {0}".format(ex), exc_info=True)
                break
            except Exception as ex:
                self.logger.error("RequestHandler:__handshake():: {0}".format(ex), exc_info=True)
                raise ex

            try:
                # print('waiting for client to send')
                buffer = self.client_connection.recv(int(os.getenv('BUFFER_SIZE')))
                print("client:", buffer)
                if not buffer: break
                connection.sendall(buffer)
            except socket.timeout as ex:
                self.logger.warn("RequestHandler:__handshake():: {0}".format(ex), exc_info=True)
            except socket.error as ex:
                self.logger.error("RequestHandler:__handshake():: {0}".format(ex), exc_info=True)
                break
            except Exception as ex:
                self.logger.error("RequestHandler:__handshake():: {0}".format(ex), exc_info=True)
                raise ex

    def start(self) -> None:
        connection = self.__connect()
        if not connection:
            print('CONNECTION FAILED')
            return None
        self.__handshake(connection)
        self.client_connection.close()
        connection.close()
        
        # proxy = self.proxyHandler.get(addrinfo[0], addrinfo[1])

        # try:
        #     _request = self.client_connection.recv(int(os.getenv('BUFFER_SIZE'))).decode('utf-8')
        #     print(_request)
        #     addrinfo = self.getaddrinfo(_request)
        #     self.client_connection.send(b"HTTP/1.1 200 Connection established\r\n\r\n")
        #     print(addrinfo[0][4])

        #     # connection = socket.create_connection(addrinfo[0][4])
        #     # connection.close()
        #     connection = socket.create_connection((self.proxy.address, self.proxy.port))
            
        #     # connection = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        #     # connection.connect()
        #     # connection.sendmsg()
        #     _request = "CONNECT https://{0}:{1} HTTP/1.1\r\n\r\n".format(addrinfo[0][4][0], addrinfo[0][4][1])
        #     _response = connection.send(_request.encode())
        #     print('connected', _response)

        #     while True:
        #         _response = connection.recv(int(os.getenv('BUFFER_SIZE')))
        #         print(_response)
        #         if not _response: break
        #         response += _response
        #         break
            
        #     self.proxy.toggleAvailable(1)
        # except socket.timeout as ex:
        #     if not response:
        #         self.logger.warning("RequestHandler:fetch():: {0}".format(ex), exc_info=True)
        # except socket.error as ex:
        #     self.logger.error("RequestHandler:fetch():: {0}".format(ex), exc_info=True)
        # except Exception as ex:
        #     self.logger.error("RequestHandler:fetch():: {0}".format(ex), exc_info=True)
        # finally:
        #     if connection:
        #         connection.close()

        # return response
