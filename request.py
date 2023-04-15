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
        retries = requests.adapters.Retry(total=3)
        if interface == None or interface == "":
            self.adapter = HTTPAdapterWithSocketOptions(max_retries=retries)
        else:
            self.adapter = HTTPAdapterWithSocketOptions(max_retries=retries, socket_options=[(
                socket.SOL_SOCKET, socket.SO_BINDTODEVICE, interface.encode('utf-8'))])
        self.session = requests.session()
        self.session.mount("http://", self.adapter)
        self.session.mount("https://", self.adapter)

    def get(self, *args, timeout=3, **kwargs):
        return self.session.get(*args, timeout=timeout, **kwargs)

    def post(self, *args, timeout=3, **kwargs):
        return self.session.post(*args, timeout=timeout, **kwargs)