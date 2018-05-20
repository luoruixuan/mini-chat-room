# -*- coding: utf-8 -*-

import json
import traceback
from project_logger import logger


class BadCmd(Exception):
    '''
    命令解释器所用的异常类
    '''
    pass


class EndSession(Exception):
    '''
    关闭会话所用的异常类
    '''
    pass


def ServerResponse(msg):
    '''
    生成一个json字符串，表示是非聊天消息的服务器响应，内容为msg
    :param msg:todo，功能待扩展
    :return:
    '''
    response_dict = dict(type='server_response', msg=msg)
    response_json = json.dumps(response_dict, encoding='utf-8', ensure_ascii='False')
    return response_json


class CommandHandler(object):
    '''
    命令解释器，用于与客户端进行交互
    '''

    def unknown(self, session, cmd_json):
        '''
        未知命令，向对方报告未知
        :param session:这个session是ChatSession实例，是一个异步套接字，用push而不是send发送
        :param cmd_json:json字符串
        :return:
        '''
        session.push(ServerResponse('Unknown command: %s' % cmd_json) + '\r\n')  # 这里用push，是async_chat的方式

    def handle(self, session, cmd_json):
        '''
        处理命令
        采用字符串json对象的形式进行消息传递
        必有属性：type，别的字段后面再议
        {
        "type": "command",
        "msg": "login",
        "timestamp": 15300000000,
        }
        {
        "type": "group_message",
        "msg": "Hello world!",
        "from": "用户1",
        "to": "组1",
        "timestamp": 15300000000,
        }
        :param session:
        :param cmd_json:
        :return:
        '''
        if not cmd_json:
            return
        try:
            cmd_dict = json.loads(cmd_json, encoding='utf-8')
            if cmd_dict['type'] == 'command':
                # 调用对应的处理函数去解决，不同层级有不同的处理函数
                # 前缀为 do_
                cmd = cmd_dict['msg'].split(' ')[0]
                method = getattr(self, 'do_' + cmd, None)
                try:
                    method(session, cmd_dict['msg'])
                except:
                    raise BadCmd

            elif cmd_dict['type'] == 'group_message':
                # 组消息
                # 将字典传给 do_group_message
                method = getattr(self, 'do_group_message', None)
                try:
                    method(session, cmd_dict)
                except:
                    raise BadCmd

            elif cmd_dict['type'] == 'single_message':
                # 一对一消息，todo
                pass
            else:
                raise BadCmd
        except Exception as err:
            logger.error("cmd_json explain error: \n%s\n%s", cmd_json, traceback.format_exc())
            self.unknown(session, cmd_json)
            return


class Room(CommandHandler):
    '''
    房间父类，继承命令解释器的功能
    不同的房间支持不同的命令
    '''

    def __init__(self, server, room_name):
        '''
        初始化房间，保存当前用户会话列表，服务器实例，房间名
        :param server:
        :param room_name:
        '''
        self.sessions = []
        self.server = server
        self.room_name = room_name

    def add(self, session):
        self.sessions.append(session)

    def remove(self, session):
        self.sessions.remove(session)

    def broadcast(self, session, line):
        '''
        广播消息给除session自己之外的所有当前房间内用户
        :param session:
        :param line:
        :return:
        '''
        for i in self.sessions:
            if i != session:
                i.push(line + '\r\n')

    def do_logout(self, session, line):
        raise EndSession


class Hall(Room):
    '''
    大厅，处理用户登入登出等
    本层支持的命令:
    login
    logout
    create_group
    create_single
    enter_group
    '''

    def add(self, session):
        '''
        新用户的会话添加到房间列表
        :param session:
        :return:
        '''
        self.sessions.append(session)
        if session.user_name == '':
            # 空用户名表示一个未注册的用户
            session.push(ServerResponse('Welcome, please login!') + '\r\n')
        else:
            session.push(ServerResponse('Back to hall.') + '\r\n')

    def do_login(self, session, line):
        '''
        处理用户登陆
        命令msg为 login name
        :param session:
        :param line:
        :return:
        '''
        parts = line.split(' ', 1)
        name = parts[1].strip()
        if not name:
            session.push(ServerResponse('Please enter username.') + '\r\n')
        elif name in self.server.active_users:
            session.push(ServerResponse('The name "%s" has been taken.\nPlease try another.') + '\r\n')
        else:
            session.user_name = name
            self.server.active_users[session.user_name] = session  # 服务器端保存新用户的名称，映射到它的会话
            session.push(ServerResponse('Login as %s.' % name) + '\r\n')

    def do_logout(self, session, line):
        '''
        处理用户登出
        命令msg为 logout
        :param session:
        :param line:
        :return:
        '''
        del self.server.active_users[session.user_name]  # 服务器活跃用户列表中删除
        self.sessions.remove(session)  # 当前房间中删除
        raise EndSession  # 抛出结束会话异常

    def do_create_group(self, session, line):
        '''
        创建一个群，并进入
        命令msg为 create_group group_name
        :param session:
        :param line:
        :return:
        '''
        group_name = line.split(' ', 1)[1]
        if group_name in self.server.group_rooms:
            session.push(ServerResponse('group %s existed' % group_name) + '\r\n')
            return
        self.server.group_rooms[group_name] = GroupRoom(self.server)  # 创建群
        session.enter(self.server.group_rooms[group_name])

    def do_enter_group(self, session, line):
        '''
        进入某一个聊天室
        命令msg为 enter_group group_name
        :param session:
        :param line:
        :return:
        '''
        group_name = line.split(' ', 1)[1]
        session.enter(self.server.group_rooms[group_name])

    def do_enter_single(self, session, line):
        '''
        单独建立一个聊天
        命令msg为 enter_single single_name
        :param session:
        :param line:
        :return:
        '''
        single_name = line.split(' ', 1)[1]
        if single_name in self.server.single_rooms:
            pass
        session.enter(self.server.single_rooms[single_name])


class GroupRoom(Room):
    '''
    群
    本层支持的命令:
    online
    back
    '''

    def add(self, session):
        '''
        添加新用户进群
        并将新用户进入的消息 广播给群内其他人
        :param session:
        :return:
        '''
        self.sessions.append(session)
        session.push(ServerResponse('Welcome to group %s!' % self.room_name) + '\r\n')
        self.broadcast(session, ServerResponse(session.user_name + ' entered the room'))

    def do_online(self, session, line):
        '''
        查看房间内有哪些其他用户
        :param session:
        :param line:
        :return:
        '''
        user_sessions = self.sessions
        session.push(ServerResponse(user_sessions) + '\r\n')

    def do_back(self, session, line):
        '''
        返回到Hall，离开群
        :param session:
        :param line:
        :return:
        '''
        session.enter(self.server.hall)
        self.sessions.remove(session)

    def do_group_message(self, session, group_msg_dict):
        '''
        {
        "type": "group_message",
        "msg": "Hello world!",
        "from": "用户1",
        "to": "组1",
        "timestamp": 15300000000,
        }
        :param session:
        :param group_msg_dict:
        :return:
        '''
        group_msg_json = json.dumps(group_msg_dict, encoding='utf-8', ensure_ascii='False')
        self.broadcast(session, group_msg_json)  # 直接把这个json转发给别的session


def SingleRoom(Room):
    '''
    一对一聊天
    :param Room:
    :return:
    '''
    pass
