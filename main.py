#!/usr/bin/python3

import crypto
import requests
import time
import re
header={
	'User-Agent':'User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:80.0) Gecko/20100101 Firefox/80.0'
}
init_url="https://auth4.tsinghua.edu.cn/srun_portal_pc.php?ac_id=1&"
get_challenge_api="http://auth4.tsinghua.edu.cn/cgi-bin/get_challenge"
get_challenge_api_6="http://auth6.tsinghua.edu.cn/cgi-bin/get_challenge"
srun_portal_api="http://auth4.tsinghua.edu.cn/cgi-bin/srun_portal"
srun_portal_api_6="http://auth6.tsinghua.edu.cn/cgi-bin/srun_portal"
n = '200'
type = '1'
ac_id = '1'
enc = "srun_bx1"
username = ""
password = ""
def get_chksum():
	chkstr = token+username
	chkstr += token+hmd5
	chkstr += token+ac_id
	chkstr += token+""
	chkstr += token+n
	chkstr += token+type
	chkstr += token+i
	return chkstr
def get_info():
	info_temp={
		"username":username,
		"password":password,
		"ip":"",
		"acid":ac_id,
		"enc_ver":enc
	}
	i=re.sub("'",'"',str(info_temp))
	i=re.sub(" ",'',i)
	return i
def get_token():
	global token
	get_challenge_params={
		"callback": "jQuery111306297270886466729_"+str(int(time.time()*1000)),
		"username":username,
		"ip":"",
		"_":int(time.time()*1000),
	}
	# print(get_challenge_params)
	get_challenge_res=requests.get(get_challenge_api,params=get_challenge_params,headers=header)
	token=re.search('"challenge":"(.*?)"',get_challenge_res.text).group(1)
def do_complex_work():
	global i,hmd5,chksum
	i = get_info()
	i="{SRBX1}"+crypto.get_base64(crypto.get_xencode(i,token))
	hmd5=crypto.get_md5(password,token)
	chksum=crypto.get_sha1(get_chksum())
def portal(action):
	srun_portal_params={
	'callback': 'jQuery111306297270886466729_'+str(int(time.time()*1000)),
	'action':action,
	'username':username,
	'password':'{MD5}'+hmd5,
	'ac_id':ac_id,
	'ip':"",
	'chksum':chksum,
	'info':i,
	'n':n,
	'type':type,
	'double_stack':'1',
	'_':int(time.time()*1000)
	}
	srun_portal_res=requests.get(srun_portal_api,params=srun_portal_params,headers=header)
	# print(srun_portal_res.text)
	print("Login IP: " + re.search('"client_ip":"(.*?)"',srun_portal_res.text).group(1))
	print(re.search('"error":"(.*?)"',srun_portal_res.text).group(1) + ". " + re.search('"error_msg":"(.*?)"',srun_portal_res.text).group(1))
	print("")

neturl = "http://net.tsinghua.edu.cn/do_login.php"
def netact(action):
	do_login_params = {
		"action": action,
		"username": username,
		"password": "{MD5_HEX}" + crypto.get_md5_hex(password),
		"ac_id": 1
	}
	login_res = requests.post(neturl, do_login_params)
	print(login_res.text)

def act(action):
	get_token()
	do_complex_work()
	portal(action)

import argparse
def parse_args(): 
	parser = argparse.ArgumentParser()
	parser.add_argument("-4", action="store_false", dest="ipv6")
	parser.add_argument("-6", action="store_false", dest="ipv4")
	parser.add_argument("-a", metavar="AC_ID", dest="ac_id", default = "1")
	parser.add_argument("-p", metavar="PASSWORD", dest="password", default = "")
	parser.add_argument("-u", metavar="USERNAME", dest="username", default = "")
	parser.add_argument("action", metavar="ACTION", default = "login")
	options = parser.parse_args()
	return options

from datetime import datetime
import sys
import os
import getpass
if __name__ == '__main__':
	print("TUNet Login Script")
	print(datetime.now())
	print("-" * 50)

	opts = parse_args()
	ac_id = opts.ac_id
	username = opts.username
	password = opts.password
	
	if username == "" and os.access("login.conf", os.R_OK): # username not passed as argument
		file = open("login.conf", mode='r')
		username=file.readline().strip()
		password=file.readline().strip()
	if username == "": # username not in config file either
		username = input("Username:").strip()
		password = getpass.getpass("Password:").strip()

	if (check()):
		exit(0)

	if (opts.ipv4 != False):
		act(opts.action)
		netact(opts.action)

	if (opts.ipv6 == False):
		exit(0)

	get_challenge_api = get_challenge_api_6
	srun_portal_api = srun_portal_api_6
	act(opts.action)
