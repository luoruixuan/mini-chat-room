# -*- coding: utf-8 -*-

import sys
import socket
import asyncore
import DataBaseInterface
from project_logger import logger
from chat_session import ChatSession
from rooms import Hall, GroupRoom


class ChatServer(asyncore.dispatcher):
    '''
    聊天服务器类，使用TCP协议、异步I/O
    数据库使用策略：
        1、建立服务器时，从数据库中读取用户列表，获得全体用户名及其密码
        2、建立服务器时，从数据库中读取群列表，建立所有的群对象
        3、用户登入时，根据数据库，初始化该用户所在的房间列表，并发最近消息给该用户（todo，传一个
        时间戳在登陆时，发这个时间之后的消息）
        4、用户的一系列操作，将会同步修改数据库内容
        5、用户登出时，不销毁数据库
    '''

    def __init__(self, host, port):
        '''
        初始化服务器，侦听用户连接请求
        保存用户名usr_name和session的映射关系，防止名字冲突
        初始化大厅Hall，以及一个群（Todo)
        :param host:
        :param port:
        '''
        asyncore.dispatcher.__init__(self)
        self.create_socket(socket.AF_INET, socket.SOCK_STREAM)
        self.set_reuse_addr()
        self.bind((host, port))
        self.listen(10)

        self.conn_sessions = []  # 连接列表
        self.active_users = {}  # 活跃用户, {"用户名": chat_session}
        self.all_users = []  # 全体用户名及其密码
        self.hall = Hall(self, 'Hall')  # 大厅，所有活跃群和活跃用户将会在这里被记录
        self.group_rooms = {}  # 群
        self.single_rooms = {}  # 一对一聊天

        self.init_users_groups()  # 初始化all_users和group_rooms

    def init_users_groups(self):
        '''
        根据数据库初始化用户、群组列表
        1、建立服务器时，从数据库中读取用户列表，获得全体用户名及其密码
        2、建立服务器时，从数据库中读取群列表，建立所有的群对象
            需要对Room.users进行初始化
        :return:
        '''
        user_query = DataBaseInterface.UserOperations()
        self.all_users = user_query.query_all().copy()  # [('lrx', '123456'), ('wy', '123456')]
        group_query = DataBaseInterface.ChatGroup('Administrator')
        # 需要获取所有群名，群主名
        group_tuples = group_query.query_all().copy()  # [('group1', 'lrx')]
        for group_tuple in group_tuples:
            self.group_rooms[group_tuple[0]] = GroupRoom(self, group_tuple[0], group_tuple[1])
        # 对每个群的users列表初始化
        for group_name in self.group_rooms.keys():
            user_members = group_query.query_members(group_name=group_name).copy()  # ['lrx', 'wy']
            self.group_rooms[group_name].users = user_members.copy()

    def handle_accept(self):
        '''
        接收用户的接入请求，每一个用户分配一个socket
        并初始化一个ChatSession
        :return:
        '''
        conn, addr = self.accept()
        chat_session = ChatSession(self, conn)
        self.conn_sessions.append(chat_session)


if __name__ == '__main__':
    # if len(sys.argv) != 3:
    #     sys.stderr.write('Usage: python3 custom_server.py <host> <port>\n')
    #     sys.exit(1)
    # host = sys.argv[1]
    # port = int(sys.argv[2])
    host = '0.0.0.0'
    port = 8080
    cus_server = ChatServer(host, port)
    try:
        asyncore.loop()  # 异步套接字侦测循环
    except KeyboardInterrupt:
        sys.stderr.write('Exit\n')
        pass
