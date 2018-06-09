# -*- coding: utf-8 -*-

import socket
import json
import threading
import time
import random
import queue
import string
from secure_transmission import *

HOST = '127.0.0.1'
PORT = 8080

class ClientSession:
    def __init__(self, host, port):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((host, port))
        self.MAX_BUFSIZE = 1024
        self.queue = queue.Queue(500)
        self.receiver = threading.Thread(target=lambda:self.recv())
        self.receiver.start()
        self.lock = threading.Lock()
        self.waiting = None
        # by lanying 
        # 随机生成字符串
        ran_str=''.join(random.sample(string.ascii_letters+string.digits,16))
        self.AESinstance=AESmessage(ran_str)
        self.RSAinstance=RSAmessage(newKey=False)
        self.AESKey_is_init=False
        # by lanying

    def recv(self):
        data = []
        while True:
            time.sleep(0.1)
            res = self.socket.recv(self.MAX_BUFSIZE)
            # by lanying
            if self.AESKey_is_init:
                res=self.AESinstance.AESDecrypt(res)
            else:
                res = bytes.decode(res, encoding='utf-8')
            # by lanying
            data.append(res)
            if res.endswith('\r\n'):
                msg = ''.join(data)
                data = []
                js = json.loads(msg.strip(), encoding='utf-8')
                print('Receive: '+str(js))
                if js['type']=='server_response':
                    if js['msg']=='please login':
                        continue
                    elif js['msg']=='AC_AESKey':    # by lanying
                        self.AESKey_is_init=True
                    self.waiting = js
                # by lanying
                elif js['type']=='init':
                    if js['msg']=='RSApubKey':
                        self.waiting = js
                        self.RSAinstance.pubKey=bytes(js['Key'],encoding='utf-8')
                        self.waiting_response=True
                        self.send_AESKey(self.AESinstance.key)
                        continue
                # by lanying
                else:
                    #self.msg_func(js)
                    self.queue.put(js)
                
            

    def __del__(self):
        self.receiver.stop()
        self.receiver.join()
        self.socket.close()

    def send(self, request):
        self.lock.acquire()
        self.waiting = None
        seq = int(time.time()*1000)
        request['timestamp'] = seq
        s = json.dumps(request, ensure_ascii=False) # json to string
        print('Send: '+s)
        # by lanying
        if self.AESKey_is_init:
            sendmsg=self.AESinstance.AESEncript(s.encode('utf-8'))
            self.socket.send(sendmsg)
            self.socket.send('\r\n'.encode('utf-8'))
        else:
            self.socket.send((s+'\r\n').encode('utf-8'))
        # by lanying
        while self.waiting is None:    # wait for response
            time.sleep(0.5)
            if self.waiting_response:
                self.waiting_response=False
                break
        res = self.waiting
        self.lock.release()
        return res

    def login(self, usr_name, pwd):
        request = {'type':'command',
                   'msg':'login',
                   'usr_name': usr_name,
                   'password': pwd}
        res = self.send(request)
        status, msg = res['status'], res['msg']
        return status, msg
        
    def logout(self, usr_name):
        request = {'type':'command',
                   'msg':'logout',
                   'usr_name': usr_name}
        res = self.send(request)
        status, msg = res['status'], res['msg']
        return status, msg

    def register(self, usr_name, pwd):
        request = {'type':'command',
                   'msg':'register',
                   'usr_name': usr_name,
                   'password': pwd}
        res = self.send(request)
        status, msg = res['status'], res['msg']
        return status, msg

    def get_friend_list(self, usr_name):
        request = {'type':'command',
                   'msg':'get_friend_list',
                   'usr_name': usr_name}
        res = self.send(request)
        status, msg = res['status'], res['msg']
        return status, msg

    def get_chat_rooms(self, usr_name):
        request = {'type':'command',
                   'msg':'get_chat_rooms',
                   'usr_name': usr_name}
        #res = self.send(request)
        #status, msg = res['status'], res['msg']
        return True, [1,2,3,4,5]
        return status, msg

    def send_friend_request(self, usr_name, friend_name, ver_msg):
        request = {'type':'command',
                   'msg':'add_friend',
                   'usr_name': usr_name,
                   'friend_name': friend_name,
                   'message':ver_msg}
        res = self.send(request)
        status, msg = res['status'], res['msg']
        return status, msg

    def create_chat_room_request(self, usr_name, group_name, password):
        request = {'type':'command',
                   'msg':'create_group',
                   'usr_name': usr_name,
                   'group_name': group_name,
                   'password': password}
        res = self.send(request)
        status, msg = res['status'], res['msg']
        return status, msg

    def enter_chat_room_request(self, usr_name, group_name, password):
        request = {'type':'command',
                   'msg':'enter_group',
                   'usr_name': usr_name,
                   'group_name': group_name,
                   'password': password}
        res = self.send(request)
        status, msg = res['status'], res['msg']
        return status, msg

    def get_room_info(self, usr_name, group_name):
        request = {'type':'command',
                   'msg':'desc_group',
                   'usr_name': usr_name,
                   'group_name': group_name}
        res = self.send(request)
        status, msg = res['status'], res['msg']
        return status, res['info']
    '''
    def get_room_files(self, group_name):
        # TODO
        lst = []
        for i in range(20):
            lst.append('%d.txt'%i)
        return True, {'files':lst}'''

    def send_msg(self, group_name, msg):
        request = {'type':'group_message',
                   'msg':msg,
                   'group_name': group_name}
        res = self.send(request)
        status, msg = res['status'], res['msg']
        return status, msg

    def leave_room(self, usr_name, group_name):
        request = {'type':'command',
                   'msg':'leave_group',
                   'usr_name': usr_name,
                   'group_name': group_name}
        res = self.send(request)
        status, msg = res['status'], res['msg']
        return status, msg

    def change_password_request(self, usr_name, old_pwd, new_pwd):
        request = {'type': 'command',
                   'msg': 'change_password',
                   'usr_name': usr_name,
                   'old_password': old_pwd,
                   'new_password': new_pwd}
        res = self.send(request)
        status, msg = res['status'], res['msg']
        return status, msg

    def add_friend_request(self, usr_name, friend_name, ver_msg):
        request = {'type': 'command',
                   'msg': 'add_friend',
                   'usr_name': usr_name,
                   'friend_name': friend_name,
                   'verification_message': ver_msg}
        res = self.send(request)
        status, msg = res['status'], res['msg']
        return status, msg

    def get_verification_message(self, usr_name):
        request = {'type': 'command',
                   'msg': 'get_verification_message',
                   'usr_name': usr_name}
        res = self.send(request)
        status, msg = res['status'], res['msg']
        return status, res['info']

    def add_friend_response(self, usr_name, friend_name, response):
        request = {'type': 'command',
                   'msg': 'add_friend_response',
                   'usr_name': usr_name,
                   'friend_name': friend_name,
                   'accept': response}
        res = self.send(request)
        status, msg = res['status'], res['msg']
        return status, msg

    def invite_friend(self, usr_name, friend_name, group_name):
        request = {'type': 'command',
                   'msg': 'invite_friend',
                   'usr_name': usr_name,
                   'friend_name': friend_name,
                   'group_name': group_name}
        res = self.send(request)
        status, msg = res['status'], res['msg']
        return status, msg

    def remove_person(self, usr_name, friend_name, group_name):
        request = {'type': 'command',
                   'msg': 'remove_person',
                   'usr_name': usr_name,
                   'friend_name': friend_name,
                   'group_name': group_name}
        res = self.send(request)
        status, msg = res['status'], res['msg']
        return status, msg

    def get_group_list(self, usr_name):
        request = {'type': 'command',
                   'msg': 'get_group_list',
                   'usr_name': usr_name}
        res = self.send(request)
        status, msg = res['status'], res['msg']
        return status, res['info']

    def get_friend_list(self, usr_name):
        request = {'type': 'command',
                   'msg': 'get_friend_list',
                   'usr_name': usr_name}
        res = self.send(request)
        status, msg = res['status'], res['msg']
        return status, res['info']

    def share_file(self, group_name, file_name, file_content):
        request = {
            'type': 'file_message',
            'file_name': file_name,
            'file_content': file_content,
            'group_name': group_name
        }
        res = self.send(request)
        status, msg = res['status'], res['msg']
        return status, msg
    
    # by lanying
    # 这里不设返回值，因为在recv里调用send，send里调用wait造成死锁，所以不等返回
    def send_AESKey(self,key):
        # 用RSA公钥加密ASE密钥并发送
        enckey=self.RSAinstance.RSAEncrypt(key)
        request = {
            'type': 'init',
            'msg': 'AESKey',
            'Key': str(enckey,encoding='utf-8')
        }
        self.send(request)

    
