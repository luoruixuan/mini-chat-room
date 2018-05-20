# -*- coding: utf-8 -*-

import socket
import asyncore
from project_logger import logger


class ChatServer(asyncore.dispatcher):
    '''
    聊天服务器类，使用TCP协议、异步I/O
    '''

    def __init__(self, host, port):
        '''
        初始化服务器，侦听用户连接请求
        保存用户名user_name和session的映射关系，防止名字冲突
        初始化大厅Hall，以及一个群（Todo)
        :param host:
        :param port:
        '''
        asyncore.dispatcher.__init__(self)
        self.create_socket(socket.AF_INET, socket.SOCK_STREAM)
        self.set_reuse_addr()
        self.bind((host, port))
        self.listen(10)
        self.active_users = {}  # 活跃用户, {"用户名": chat_session}
        self.hall = object()  # 大厅，所有活跃群和活跃用户将会在这里被记录
        self.group_rooms = {} # 群
        self.single_rooms = {} # 一对一聊天

    def handle_accept(self):
        '''
        接收用户的接入请求，每一个用户分配一个socket
        并初始化一个ChatSession
        :return:
        '''
        conn, addr = self.accept()

    pass
