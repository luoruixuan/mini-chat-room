# -*- coding: utf-8 -*-

import socket
import json
import threading
import time
import random

HOST = '127.0.0.1'
PORT = 8080

class ClientSession:
    def __init__(self, host, port):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((host, port))
        self.MAX_BUFSIZE = 1024
        self.msg_func = None
        self.receiver = threading.Thread(target=lambda:self.recv())
        self.receiver.start()
        self.waiting = {}
        self.now = random.randint(0, 65535)

    def recv(self):
        data = []
        while True:
            time.sleep(0.1)
            res = self.socket.recv(self.MAX_BUFSIZE)
            data.append(res)
            if res.endswith('\r\n'):
                msg = ''.join(data)
                data = []
                js = json.loads(msg.strip(), encoding='utf-8')
                if js['type']=='response':
                    self.waiting[js['seq']] = js
                else:
                    self.msg_func(js)
                
            

    def __del__(self):
        self.receiver.stop()
        self.receiver.join()
        self.socket.close()

    def send(self, request):
        seq = self.now
        request['seq'] = seq
        self.now += 1
        self.waiting[seq] = None
        s = json.dumps(request) # json to string
        self.socket.send(s.encode('utf-8'))
        while self.waiting[seq] is None:    # wait for response
            time.sleep(0.5)
        res = self.waiting[seq]
        self.waiting.pop(seq)
        return res

    def login(self, usr_name, pwd):
        request = {'type':'command',
                   'msg':'login',
                   'usr_name': usr_name,
                   'password': pwd}
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

    def create_chat_room_request(self, usr_name):
        request = {'type':'command',
                   'msg':'create_chat_room',
                   'usr_name': usr_name}
        res = self.send(request)
        status, msg = res['status'], res['msg']
        return status, msg

    def enter_chat_room_request(self, usr_name, room_id, password):
        request = {'type':'command',
                   'msg':'enter_chat_room',
                   'usr_name': usr_name,
                   'room_id':room_id,
                   'password':password}
        res = self.send(request)
        status, msg = res['status'], res['msg']
        return status, msg

    def get_room_info(self, cid):
        request = {'type':'command',
                   'msg':'get_room_info',
                   'room_id':cid}
        #res = self.send(request)
        #status, msg = res['status'], res['msg']
        return True, {'creator':'233', 'name':'hahaha', 'ID':1, 'members':['aaa','bbb','ccc']}
        return status, msg

    def send_msg(self, cid, msg):
        request = {'type':'group_message',
                   'msg':msg,
                   'room_id':cid}
        res = self.send(request)
        status, msg = res['status'], res['msg']
        return status, msg

    def leave_room(self, usr_name, room_id):
        request = {'type':'command',
                   'msg':'leave_chat_room',
                   'usr_name': usr_name,
                   'room_id':room_id}
        res = self.send(request)
        status, msg = res['status'], res['msg']
        return status, msg

    
