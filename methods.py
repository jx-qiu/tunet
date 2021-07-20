"""
This file specifies all the available methods of connection to TUNet.
"""

import crypto
from request import Request
import time
import re

class Connector():
    """
    Abstract connector interface.
    """
    header = {
        'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:90.0) Gecko/20100101 Firefox/90.0'
    }
    
    def __init__(self, username: str, password: str):
        self.username = username
        self.password = password
        self.requests = Request("")

    def connect(self):
        return True

    def disconnect(self):
        return True

    def set_interface(self, interface: str):
        self.requests = Request(interface)

class NetTsinghuaConnector(Connector):
    """
    Connector that uses net.tsinghua.edu.cn as portal.
    """
    url = "http://net.tsinghua.edu.cn/do_login.php"

    def __init__(self, username, password):
        super().__init__(username, password)

    def connect(self):
        params = {
            "action": "login",
            "username": self.username,
            "password": "{MD5_HEX}" + crypto.get_md5_hex(self.password),
            "ac_id": 1
        }
        res = self.requests.post(self.url, params, headers=self.header)
        print(res.text)

    def disconnect(self):
        params = {
            "action": "logout"
        }
        res = self.requests.post(self.url, params, headers=self.header)
        print(res.text)

class AuthTsinghuaConnector(Connector):
    """
    Connector that uses auth{4,6}.tsinghua.edu.cn as portal.
    """
    get_challenge_api = "http://auth4.tsinghua.edu.cn/cgi-bin/get_challenge"
    get_challenge_api_6 = "http://auth6.tsinghua.edu.cn/cgi-bin/get_challenge"
    srun_portal_api = "http://auth4.tsinghua.edu.cn/cgi-bin/srun_portal"
    srun_portal_api_6 = "http://auth6.tsinghua.edu.cn/cgi-bin/srun_portal"
    n = '200'
    type = '1'
    enc = "srun_bx1"

    def __init__(self, username, password):
        super().__init__(username, password)
        self.ac_id = "1"
        self.update_acid()

    def set_interface(self, interface: str):
        self.requests = Request(interface)
        self.update_acid()
    
    def update_acid(self):
        results = self.requests.get("http://net.tsinghua.edu.cn")
        results = re.search("index_([0-9]+).html", results.text)
        if (results != None):
            self.ac_id = results.group(1)

    def connect(self):
        self.act("login")
        return True

    def disconnect(self):
        self.act("logout")
        return True

    def act(self, action: str):
        get_challenge_params = {
            "callback": "jQuery111306297270886466729_"+str(int(time.time()*1000)),
            "username": self.username,
            "ip": "",
            "_": int(time.time()*1000),
        }
        # print(get_challenge_params)
        get_challenge_res = self.requests.get(
            self.get_challenge_api, params=get_challenge_params, headers=self.header)
        token = re.search('"challenge":"(.*?)"', get_challenge_res.text).group(1)

        i = self.get_info()
        i = "{SRBX1}"+crypto.get_base64(crypto.get_xencode(i, token))
        hmd5 = crypto.get_md5(self.password, token)
        chkstr = token+self.username
        chkstr += token+hmd5
        chkstr += token+self.ac_id
        chkstr += token+""
        chkstr += token+self.n
        chkstr += token+self.type
        chkstr += token+i
        chksum = crypto.get_sha1(chkstr)

        srun_portal_params = {
            'callback': 'jQuery111306297270886466729_'+str(int(time.time()*1000)),
            'action': action,
            'username': self.username,
            'password': '{MD5}'+hmd5,
            'ac_id': self.ac_id,
            'ip': "",
            'chksum': chksum,
            'info': i,
            'n': self.n,
            'type': self.type,
            'double_stack': '1',
            '_': int(time.time()*1000)
        }
        srun_portal_res = self.requests.get(
            self.srun_portal_api, params=srun_portal_params, headers=self.header)
        # print(srun_portal_res.text)
        print("Login IP: " + re.search('"client_ip":"(.*?)"',
            srun_portal_res.text).group(1))
        print(re.search('"error":"(.*?)"', srun_portal_res.text).group(1) +
            ". " + re.search('"error_msg":"(.*?)"', srun_portal_res.text).group(1))
        print("")

    def get_info(self):
        info_temp = {
            "username": self.username,
            "password": self.password,
            "ip": "",
            "acid": self.ac_id,
            "enc_ver": self.enc
        }
        i = re.sub("'", '"', str(info_temp))
        i = re.sub(" ", '', i)
        return i

