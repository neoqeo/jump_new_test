# -*- coding: utf-8 -*-
"""
Created on Mon Apr 03 21:24:18 2017

@author: Selay
@updater" JohnN

"""

import requests
import json
import threading
import sys
import os
import argparse
# 字典allusers用于存储 由 索引名和openID构成的键值对
# 微信关注‘测试号’时，会生成openID用于与对应微信账号通讯
# 索引名 是为了便于自己识别和管理而对openID起的别名

allusers = {'John':'oDGoDw4hEzv6cXmAJzzSUt9UCoag'}

def usersto(users = None):
    if users == None:
        return allusers['John']
    elif users == "All":
        return ','.join(set(allusers.values()))
    else:
        if isinstance(users,list):
            usersinfo = []
            for user in users:
                usersinfo.append(allusers[user])
            return ','.join(set(usersinfo))
        else:
            print ("'users' must be a list!")
            return


def json_post_data_generator(content='Hi',users = None):
    content_data = content.split('-@@-')
    notify_type = content_data[0]
    if notify_type == 'host':
        type1 = content_data[1]
        host_name = content_data[2]
        host_state = content_data[3]
        host_address = content_data[4]
        host_info = content_data[5]
        content = "**** Nagios ****\n\nNotification Type: " + type1 + \
                         "\nHost: " + host_name + \
                         "\nState: " + host_state + \
                         "\nAddress: " + host_address + \
                         "\nInfo: " + host_info + "\n"
    elif notify_type == 'service':
        type1 = content_data[1]
        service_desc = content_data[2]
        host_name = content_data[3]
        host_address = content_data[4]
        service_state = content_data[5]
        service_info = content_data[6]
        content = "**** Nagios ****\n\nNotification Type: " + type1 + \
                         "\nService: " + service_desc + \
                         "\nHost: " + host_name + \
                         "\nAddress: " + host_address + \
                         "\nState: " + service_state + \
                         "\nInfo: " + service_info + "\n"
    else:
        content = "Get nagios message notify info error.\n\nContent: %s" % content

    msg_content = {}
    msg_content['content'] = content
    post_data = {}
    post_data['text'] = msg_content
    post_data['touser'] = "%s" % usersto(users)
    post_data['toparty'] = ''
    post_data['msgtype'] = 'text'
    post_data['agentid'] = '9'
    post_data['safe'] = '0'
    #由于字典格式不能被识别，需要转换成json然后在作post请求
    #注：如果要发送的消息内容有中文的话，第三个参数一定要设为False
#    return json.dumps(post_data,False,False)
    return json.dumps(post_data)
# 需将此处的APPID,APPSECRET换为自己‘测试号管理’页面内显示的内容
def appInfos():
    APPID = "wxfb41206c056eb4f0"
    APPSECRET = "33e1dce5cab84380b57944c079c737d5"
    return (APPID,APPSECRET)

def get_token_info():
    APPInfo = appInfos()
    r = requests.get("https://api.weixin.qq.com/cgi-bin/token?grant_type=client_credential&appid=%s&secret=%s" % APPInfo)
    #print "Accessing %s" %r.url
    js =  r.json()
    if "errcode" not in js:
        access_token = js["access_token"]
        expires_in = js["expires_in"]
    else:
        print ("Can not get the access_token")
        print (js)
        quit()
    return access_token,expires_in

post_url_freshing = ['']

def post_url():
    access_token,expires_in = get_token_info()
    print ("token expires_in:%s" % expires_in)
    print("token is: %s" %access_token)
    timer = threading.Timer((expires_in-200),post_url)
    timer.start()
    post_url_freshing[0] = 'https://api.weixin.qq.com/cgi-bin/message/custom/send?access_token=%s' %access_token

post_url()

def sender(text_str,user_lis = None):
    posturl = post_url_freshing[0]
    post_data = json_post_data_generator(content=text_str,users = user_lis)
    r = requests.post(posturl,data=post_data)
    result = r.json()
    if result["errcode"] == 0:
        print ("Sent successfully")
        os._exit(0)
    else:
        print ("Error msg IS: %s" %result["errmsg"])
        os._exit(1)

if __name__ == "__main__":
    #text_str = "A greeting from Python~"
    parser = argparse.ArgumentParser(description="Nagios notify by weixin")
    parser.add_argument("content", default=None, help="notify content,split with -@@-")
    args = parser.parse_args()
    text_str = args.content
    user_lis = None
sender(text_str,user_lis)
