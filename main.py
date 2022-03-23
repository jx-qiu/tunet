#!/usr/bin/python3

from datetime import datetime
import argparse
import methods
import getpass
import os
from request import Request
import re
import logging as log
import traceback

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("-4", action="store_false", dest="ipv4")
    parser.add_argument("-6", action="store_false", dest="ipv6")
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

    requests = Request(interface)
    
    # try connecting
    connector = None
    try:
        results = requests.get("http://net.tsinghua.edu.cn", timeout=5)
        if results.ok and re.search("wired", results.url) != None:
            connector = methods.NetTsinghuaConnector(username, password)
        elif results.ok and re.search("auth4", results.url + results.text) != None:
            connector = methods.AuthTsinghuaConnector(username, password)
        else: #fallback to default
            log.warn("Unable to parse portal message, falling back to default ...")
            connector = methods.AuthTsinghuaConnector(username, password)
    except: # cannot even connect to the portal, abort
        log.error("Cannot connect to portal!")
        log.error(traceback.format_exc())
        exit(1)
         
    connector.set_interface(interface)

    if action == "login":
        connector.connect()
    elif action == "logout":
        connector.disconnect()
    else:
        log.error("Action '{}' not supported!".format(action))

    # print current ip
    try:
        results = requests.get("https://checkip.amazonaws.com", timeout=5)
        log.info("Current IP: " + results.text)
    except:
        log.warn("Warning: Unable to obtain current IP!")
        log.warn(traceback.format_exc())
