# -*- coding: utf-8 -*-

import socket
import json
import threading
import time
import random
import queue

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

    def recv(self):
        data = []
        while True:
            time.sleep(0.1)
            res = self.socket.recv(self.MAX_BUFSIZE)
            res = bytes.decode(res, encoding='utf-8')
            data.append(res)
            if res.endswith('\r\n'):
                msg = ''.join(data)
                data = []
                js = json.loads(msg.strip(), encoding='utf-8')
                print('Receive: '+str(js))
                if js['type']=='server_response':
                    if js['msg']=='please login':
                        continue
                    self.waiting = js
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
        s = json.dumps(request, ensure_ascii=False)+'\r\n' # json to string
        print('Send: '+s)
        self.socket.send(s.encode('utf-8'))
        while self.waiting is None:    # wait for response
            time.sleep(0.5)
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

    
