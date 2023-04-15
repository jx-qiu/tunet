import requests
import socket


class HTTPAdapterWithSocketOptions(requests.adapters.HTTPAdapter):
    def __init__(self, *args, **kwargs):
        self.socket_options = kwargs.pop("socket_options", None)
        super(HTTPAdapterWithSocketOptions, self).__init__(*args, **kwargs)

    def init_poolmanager(self, *args, **kwargs):
        if self.socket_options is not None:
            kwargs["socket_options"] = self.socket_options
        super(HTTPAdapterWithSocketOptions,
              self).init_poolmanager(*args, **kwargs)

class Request():
    
    def __init__(self, interface: str) -> None:
        if interface == None or interface == "":
            self.adapter = HTTPAdapterWithSocketOptions()
        else:
            self.adapter = HTTPAdapterWithSocketOptions(socket_options=[(
                socket.SOL_SOCKET, socket.SO_BINDTODEVICE, interface.encode('utf-8'))], max_retries=3)
        self.session = requests.session()
        self.session.mount("http://", self.adapter)
        self.session.mount("https://", self.adapter)
    
    def get(self, *args, **kwargs):
        return self.session.get(*args, **kwargs)

    def post(self, *args, **kwargs):
        return self.session.post(*args, **kwargs)
