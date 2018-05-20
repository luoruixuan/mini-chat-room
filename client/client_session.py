# -*- coding: utf-8 -*-

import socket
import json

HOST = '127.0.0.1'
PORT = 8080

class ClientSession:
    def __init__(self, host, port):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((host, port))
        self.MAX_BUFSIZE = 1024

    def __del__(self):
        self.socket.close()

    def send(self, request):
        s = json.dumps(request) # json to string
        self.socket.send(s)
        res = self.socket.recv(self.MAX_BUFSIZE)
        return json.loads(res)

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

    def get_friend_list(self, name):
        request = {'type':'command',
                   'msg':'get_friend_list',
                   'usr_name': usr_name}
        res = self.send(request)
        status, msg = res['status'], res['msg']
        return status, msg

    def get_chat_rooms(self, name):
        request = {'type':'command',
                   'msg':'get_chat_rooms',
                   'usr_name': usr_name}
        res = self.send(request)
        status, msg = res['status'], res['msg']
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

    
