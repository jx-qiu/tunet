#!/usr/bin/python3

from datetime import datetime
import argparse
import methods
import getpass
import os
from request import Request
import re


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("-4", action="store_false", dest="ipv6")
    parser.add_argument("-6", action="store_false", dest="ipv4")
    parser.add_argument("-i", metavar="INTERFACE", dest="interface", default="")
    parser.add_argument("-p", metavar="PASSWORD", dest="password", default="")
    parser.add_argument("-u", metavar="USERNAME", dest="username", default="")
    parser.add_argument("action", metavar="ACTION", default="login", nargs='?')
    options = parser.parse_args()
    return options


if __name__ == '__main__':
    print("TUNet Login Script")
    print(datetime.now())
    print("-" * 50)

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
            connector = methods.AuthTsinghuaConnector(username, password)
    except: # cannot even connect to the portal, abort
        print("Error: Cannot connect to portal!")
        exit(1)
         
    connector.set_interface(interface)

    if action == "login":
        connector.connect()
    elif action == "logout":
        connector.disconnect()
    else:
        print("Error: Action '{}' not supported!".format(action))

    # print current ip
    try:
        results = requests.get("https://checkip.amazonaws.com")
        print("Current IP: " + results.text)
    except:
        print("Warning: Unable to obtain current IP!")
