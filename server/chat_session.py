# -*- coding: utf-8 -*-

import asynchat
from project_logger import logger
from rooms import EndSession


class ChatSession(asynchat.async_chat):
    '''
    处理与单个用户的通信会话，将socket变为异步的
    '''

    def __init__(self, server, sock):
        asynchat.async_chat.__init__(self, sock)  # 用socket实例化一个async_chat
        self.server = server
        self.set_terminator('\r\n')  # 消息终止标志\r\n
        self.data = []  # 数据缓冲区（一次接收的消息可能不完整，用缓冲区存直到出现终止符）
        self.user_name = ''  # 用户名

    def enter(self, room):
        '''
        进入某一个房间，可以是群聊房间，也可以是大厅，todo，一对一房间
        todo 目前一个用户只能在一个房间里
        :param room:
        :return:
        '''
        self.room = room
        room.add(self)  # 一个session代表一个用户，加到房间里

    def collect_incoming_data(self, data):
        '''
        缓存从用户收到的数据
        :param data:
        :return:
        '''
        self.data.append(data)

    def found_terminator(self):
        '''
        发现了terminator，设置的是\r\n
        则将从用户接收到的消息 发给 当前所在房间的 命令解释器处理
        :return:
        '''
        line = ''.join(self.data)  # 整理收到的这些消息
        self.data = []  # 清空数据缓冲区，以准备接受下一次消息

        try:
            self.room.handle(self, line)  # 当前所在房间的命令解释器解释这条消息
        except EndSession:
            self.handle_close()  # 抛出结束会话的异常，则断开这个session

    def handle_close(self):
        asynchat.async_chat.handle_close(self)
