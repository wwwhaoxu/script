#!/usr/bin/python
# -*-coding:utf-8-*-
import sys
import os
import urllib2
import json
reload(sys)
sys.setdefaultencoding('utf8')


single_login = "https://yth.mvwchina.com/rest/studentInfo/selectList"
values = {"account":"医视界医院","password":"000000"}
jdata = json.dump(values)
req = urllib2.Request(single_login,jdata)
response = urllib2.urlopen(req)
print(response.read())
