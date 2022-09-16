#!/usr/bin/python3

import argparse
import getpass
import logging as log
import os
import re
import traceback
from datetime import datetime

import methods
from request import Request


def parse_args():
    parser = argparse.ArgumentParser()
    # parser.add_argument("-4", action="store_false", dest="ipv4")
    # parser.add_argument("-6", action="store_false", dest="ipv6")
    parser.add_argument("-i", metavar="INTERFACE", dest="interface", default="")
    parser.add_argument("-p", metavar="PASSWORD", dest="password", default="")
    parser.add_argument("-u", metavar="USERNAME", dest="username", default="")
    parser.add_argument("action", metavar="ACTION", default="login", nargs='?')
    options = parser.parse_args()
    return options


if __name__ == '__main__':
    os.environ['no_proxy'] = '*'
   
    log.basicConfig(level=log.INFO,
                format='%(asctime)s - %(levelname)s: %(message)s')

    log.info("TUNet Login Script")
    log.info(datetime.now())
    log.info("-" * 50)

    opts = parse_args()
    action = opts.action
    interface = opts.interface
    username = opts.username
    password = opts.password

    # username not passed as argument
    if username == "" and os.access("login.conf", os.R_OK):
        file = open("login.conf", mode='r')
        username = file.readline().strip()
        password = file.readline().strip()
    if username == "":  # username not in config file either
        username = input("Username:").strip()
        password = getpass.getpass("Password:").strip()
    
    if action == "login":
        try:
            methods.NetTsinghuaConnector(username, password, interface).connect()
        except:
            pass
        try:
            methods.AuthTsinghuaConnector(username, password, interface).connect()
        except:
            pass
    elif action == "logout":
        try:
            methods.NetTsinghuaConnector(username, password, interface).disconnect()
        except:
            pass
        try:
            methods.AuthTsinghuaConnector(username, password, interface).disconnect()
        except:
            pass
    else:
        log.error("Action '{}' not supported!".format(action))

    # print current ip
    requests = Request(interface)
    try:
        results = requests.get("https://checkip.amazonaws.com", timeout=5)
        log.info("Current IP: " + results.text)
    except:
        log.warn("Warning: Unable to obtain current IP!")
        log.warn(traceback.format_exc())
