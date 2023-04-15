#!/usr/bin/python3

from datetime import datetime
import argparse
import methods
import getpass
import os
import sys
import crypto
import requests
import time
import re

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("-4", action="store_false", dest="ipv6")
    parser.add_argument("-6", action="store_false", dest="ipv4")
    parser.add_argument("-a", metavar="AC_ID", dest="ac_id", default="1")
    parser.add_argument("-p", metavar="PASSWORD", dest="password", default="")
    parser.add_argument("-u", metavar="USERNAME", dest="username", default="")
    parser.add_argument("action", metavar="ACTION", default="login", nargs='*')
    options = parser.parse_args()
    return options


def check():
    testURL = "https://www.baidu.com"
    try:
        # use https, for http might suffer MITM
        results = requests.get(testURL)
        if results.ok:  # connection successful
            return True

        return False
    except requests.exceptions.RequestException as e:
        return False


if __name__ == '__main__':
    print("TUNet Login Script")
    print(datetime.now())
    print("-" * 50)

    opts = parse_args()
    action = opts.action[0]
    ac_id = opts.ac_id
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

    # if (check()):
    #     print("Connection test successful, no actions needed.")
    #     exit(0)

    # no network connection, try connecting
    connector = None
    try:
        results = requests.get("http://net.tsinghua.edu.cn")
        if results.ok and re.search("auth4", results.url) != -1:
            connector = methods.AuthTsinghuaConnector(username, password)
        if results.ok and re.search("wired", results.url) != None:
            connector = methods.NetTsinghuaConnector(username, password)
    except: # fallback to default
        connector = methods.AuthTsinghuaConnector(username, password)
    
    if action == "login":
        connector.connect()
        if (check()):
            print("Connection successful.")
            exit(0)
        else:
            print("Connection failed.")
            exit(1)
    elif action == "logout":
        connector.disconnect()
    else:
        print("Action '{}' not supported!".format(action))

