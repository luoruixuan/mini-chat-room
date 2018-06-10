# -*- coding: utf-8 -*-

import asynchat
import asyncore
import json
import traceback
from project_logger import logger
from rooms import EndSession
from secure_transmission import *


class FileSession(asyncore.dispatcher_with_send):
    '''
    用于给文件传输打开单独的通信会话
    '''

    def __init__(self, server, sock):
        pass

    pass


class ChatSession(asynchat.async_chat):
    '''
    处理与单个用户的通信会话，将socket变为异步的
    这个会话类型用于chat-style (command/response) protocols
    因此文件协议需要另外的设计
    '''

    def __init__(self, server, sock):
        asynchat.async_chat.__init__(self, sock)  # 用socket实例化一个async_chat
        self.server = server
        self.set_terminator('\r\n'.encode('utf-8'))  # 消息终止标志\r\n
        self.data = []  # 数据缓冲区（一次接收的消息可能不完整，用缓冲区存直到出现终止符）
        self.usr_name = ''  # 用户名
        self.entered_rooms = {}  # 保存当前用户所在房间， {"房间名": room对象}
        self.room_judger = RoomJudger()  # 用于判断应该去哪个房间执行命令

        self.enter(self.server.hall)  # 创建session之后就进入大厅
        # by lanying 
        self.AESKey_is_init = False
        self.RSAinstance = RSAmessage()
        self.AESinstance = AESmessage('')
        send_dict = dict(type='init', msg='RSApubKey', Key=str(self.RSAinstance.pubKey, encoding='utf-8'))
        send_json = json.dumps(send_dict)
        self.SecurityPush((send_json + '\r\n').encode('utf-8'))
        # by lanying

    def enter(self, room):
        '''
        进入某一个房间，可以是群聊房间，也可以是大厅，todo，一对一房间
        :param room:
        :return:
        '''
        if room.room_name in self.entered_rooms:
            # 已经在该房间中了
            return
        self.entered_rooms[room.room_name] = room  # 保存这个对象
        self.entered_rooms[room.room_name].add_session(self)  # 一个session代表一个用户，加到房间里

    def collect_incoming_data(self, data):
        '''
        缓存从用户收到的数据
        转码成 unicode
        :param data:
        :return:
        '''
        # by lanying
        if self.AESKey_is_init:
            data = self.AESinstance.AESDecrypt(data)
            self.data.append(data)
        else:
            self.data.append(data.decode('utf-8'))
            # by lanying

    def found_terminator(self):
        '''
        发现了terminator，设置的是\r\n
        则将从用户接收到的消息 发给 对应的房间的 命令解释器 处理
        :return:
        '''
        line = ''.join(self.data)  # 整理收到的这些消息
        self.data = []  # 清空数据缓冲区，以准备接受下一次消息

        # 需要知道是去哪个房间找
        room_name = self.room_judger.get_room_name(line)
        try:
            self.entered_rooms[room_name].handle(self, line)  # 对应房间的命令解释器解释这条消息
        except EndSession:
            self.handle_close()  # 抛出结束会话的异常，则断开这个session

    def handle_close(self):
        asynchat.async_chat.handle_close(self)

    # by lanying
    def SecurityPush(self, sendbuffer):
        if self.AESKey_is_init:
            sendbuffer = self.AESinstance.AESEncript(str(sendbuffer, encoding='utf-8'))
        else:
            pass
        self.push(sendbuffer)
        # by lanying


class RoomJudger(object):
    '''
    由于一个session可以在多个房间里，因此需要确定命令具体应该发给哪个房间
    '''

    def __init__(self):
        # 除了以下这些命令，都能找到 group_name 字段
        self.hall_commands = ['login', 'register', 'logout', 'change_password', 'create_group',
                              'enter_group', 'add_friend', 'get_verification_message',
                              'add_friend_response', 'get_group_list', 'get_friend_list']

    def get_room_name(self, line):
        '''
        根据一条消息，得出room_name
        :param line:
        :return:
        '''
        try:
            cmd_dict = json.loads(line, encoding='utf-8')
            if cmd_dict['type'] == 'init':
                return 'Hall'
            if cmd_dict['type'] == 'command':
                if cmd_dict['msg'] in self.hall_commands:
                    return 'Hall'
            return cmd_dict['group_name']
        except Exception as err:
            logger.error("cannot get room_name: \n%s\n%s", line, traceback.format_exc())
            return 'Hall'  # 未知的就发往hall去处理
