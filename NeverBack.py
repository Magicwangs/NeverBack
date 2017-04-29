# -*- coding: utf-8 -*-
"""
Created on Fri Apr 28 19:46:27 2017

@author: MagicWang
"""
import os
import re
import shutil
import time
import itchat
import requests
from itchat.content import *


msg_dict = {}
WantedNickName = u"测试群"
tulingKey = 'c8f33dcfbccd49cf8c416283258bee97'


#只接受好友，不接受群组，公众号消息
#接受文本
@itchat.msg_register([TEXT], isGroupChat = False, isFriendChat = True, isMpChat=False)
def TulingFriend(msg):
    apiUrl = 'http://www.tuling123.com/openapi/api'
    msg_content = msg['Content']
    data = {
        'key'    : tulingKey,
        'info'   : msg_content,
        'userid' : 'wechat-robot'
        }
    try:
        r = requests.post(apiUrl, data = data).json()
        return r.get('text')
    except:
        return "我断网了！！"


#ClearTimeOutMsg用于清理消息字典，把超时消息清理掉
#为减少资源占用，此函数只在有新消息动态时调用
def ClearTimeOutMsg():
    if msg_dict.__len__() > 0:
        for msgid in list(msg_dict): #由于字典在遍历过程中不能删除元素，故使用此方法
            if time.time() - msg_dict.get(msgid, None)["time"] > 120.0: #超时两分钟
                item = msg_dict.pop(msgid)
                #print("超时的消息：", item['msg_content'])
                #可下载类消息，并删除相关文件
                if item['type'] == "Picture" \
                        or item['type'] == "Recording" \
                        or item['type'] == "Video" \
                        or item['type'] == "Attachment":
                    print("要删除的文件：", item['content'])
                    os.remove(item['content'])


#只接受群消息，不接受好友，公众号消息
#接受文本，图片(表情)，语音
@itchat.msg_register([TEXT, PICTURE], isGroupChat= True, isFriendChat=False, isMpChat=False)
def Revocation(msg):
#    print msg
#    print "\n\n"
    
    chatRoom = itchat.search_chatrooms(userName=msg['FromUserName'])
    if chatRoom['NickName'] == WantedNickName:
        msg_from = chatRoom['UserName'] ## 获取群聊
        msg_id = msg['MsgId']
        msg_from_userName = msg['ActualNickName'] #发消息的人名
        msg_time = msg['CreateTime'] #消息时间
        
        msg_content = None
        msg_type = msg['Type']
        
        if msg['Type'] == 'Text':
            msg_content = msg['Text']
        elif msg['Type'] == 'Picture':
            msg_content = msg['FileName']
            msg['Text'](msg['FileName'])

        
        msg_dict.update(
            {msg_id: {"From": msg_from, "userName": msg_from_userName, 
                        "content": msg_content, "type": msg_type, "time": msg_time}})
        ClearTimeOutMsg()
    

@itchat.msg_register([NOTE], isGroupChat=True, isFriendChat=False, isMpChat=False)
def ReturnMsg(msg):
    
    if not os.path.exists(".\\Revocation\\"):
        os.mkdir(".\\Revocation\\")
#    print msg
    chatRoom = itchat.search_chatrooms(userName=msg['FromUserName'])
    if chatRoom['NickName'] == WantedNickName:
        if re.search(r"\<sysmsg type=\"revokemsg\"\>", msg['Content']) != None:
            old_msg_id = re.search("\<msgid\>(.*?)\<\/msgid\>", msg['Content']).group(1)
            old_msg = msg_dict.get(old_msg_id, {})
    #        print(old_msg_id, old_msg)
            msg_send =  old_msg.get('userName', None) + u" 的撤回消息为:"
            
            if old_msg['type'] == 'Picture':
#                msg_send += u", 存储在当前目录下Revocation文件夹中"
                shutil.move(old_msg['content'], r".\\Revocation\\")
                itchat.send(msg_send, toUserName=old_msg.get("From"))
                sendDir = u'.\\Revocation\\'+ old_msg.get('content', None)
                itchat.send_image(sendDir, toUserName=old_msg.get("From"))
            else:    
                msg_send += old_msg.get('content', None)
                itchat.send(msg_send, toUserName=old_msg.get("From"))
            ClearTimeOutMsg()



if __name__ == "__main__":
    itchat.auto_login(hotReload=True)
    itchat.run()