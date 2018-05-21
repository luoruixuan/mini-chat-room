# -*- coding: utf-8 -*-

# todo
# 1、所有的时间戳都没考虑

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


def ServerResponse(msg, status=True, info=''):
    '''
    生成一个json字符串，表示是非聊天消息的服务器响应，内容为msg
    :param msg:todo，功能待扩展
    :param status:True or False 表明命令成功或者失败
    :param info: 额外信息
    :return:
    '''
    response_dict = dict(type='server_response', status=status, msg=msg, info=info)
    response_json = json.dumps(response_dict, ensure_ascii=False)
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
        session.push((ServerResponse('bad command', False) + '\r\n').encode('utf-8'))  # 这里用push，是async_chat的方式

    def handle(self, session, cmd_json):
        '''
        处理命令
        采用字符串json对象的形式进行消息传递
        必有属性：type，别的字段后面再议
        见used_jsons.py
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
                method = getattr(self, 'do_' + cmd_dict['msg'], None)
                try:
                    method(session, cmd_dict)  # 把字典传进去
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
                i.push((line + '\r\n').encode('utf-8'))

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
        新用户的会话出现，加到大厅里
        或者一个用户从某一个房间内返回大厅
        :param session:
        :return:
        '''
        self.sessions.append(session)
        if session.user_name == '':
            # 空用户名表示一个未注册的用户
            session.push((ServerResponse('please login') + '\r\n').encode('utf-8'))
        else:
            session.push((ServerResponse('back to hall') + '\r\n').encode('utf-8'))

    def do_login(self, session, cmd_dict):
        '''
        处理用户登陆命令
        :param session:
        :param cmd_dict:
        :return:
        '''
        name = cmd_dict['user_name']
        if not name:
            session.push((ServerResponse('user_name empty', False) + '\r\n').encode('utf-8'))
        elif name in self.server.active_users:
            session.push((ServerResponse('user_name exist', False) + '\r\n').encode('utf-8'))
        else:
            session.user_name = name
            self.server.active_users[session.user_name] = session  # 服务器端保存新用户的名称，映射到它的会话
            session.push((ServerResponse('Succeed.') + '\r\n').encode('utf-8'))

    def do_logout(self, session, cmd_dict):
        '''
        处理用户登出
        :param session:
        :param cmd_dict:
        :return:
        '''
        del self.server.active_users[session.user_name]  # 服务器活跃用户列表中删除
        self.sessions.remove(session)  # 大厅中删除
        session.push((ServerResponse('Succeed.') + '\r\n').encode('utf-8'))
        raise EndSession  # 抛出结束会话异常

    def do_create_group(self, session, cmd_dict):
        '''
        创建一个群，并进入（成为群主）
        :param session:
        :param cmd_dict:
        :return:
        '''
        group_name = cmd_dict['group_name']
        if group_name in self.server.group_rooms:
            session.push((ServerResponse('group exist', False) + '\r\n').encode('utf-8'))
            return
        self.server.group_rooms[group_name] = GroupRoom(self.server, group_name, session.user_name)  # 创建群
        self.sessions.remove(session)  # 大厅中删除
        session.enter(self.server.group_rooms[group_name])
        session.push((ServerResponse('Succeed.') + '\r\n').encode('utf-8'))

    def do_enter_group(self, session, cmd_dict):
        '''
        进入一个群
        :param session:
        :param cmd_dict:
        :return:
        '''
        group_name = cmd_dict['group_name']
        if group_name not in self.server.group_rooms:
            session.push((ServerResponse('group not exist', False) + '\r\n').encode('utf-8'))
            return
        self.sessions.remove(session)  # 大厅中删除
        session.enter(self.server.group_rooms[group_name])
        session.push((ServerResponse('Succeed.') + '\r\n').encode('utf-8'))

        # 告知群内其他人，这个在GroupRoom.add()方法内完成

    def do_enter_single(self, session, cmd_dict):
        '''
        建立一对一聊天
        :param session:
        :param cmd_dict:
        :return:
        '''
        session.push((ServerResponse('not implemented', False) + '\r\n').encode('utf-8'))
        pass


class GroupRoom(Room):
    '''
    群
    本层支持的命令:
    desc_group
    leave_group
    '''

    def __init__(self, server, room_name, creator):
        '''
        群初始化，额外加一个群主参数
        :param server:
        :param room_name:
        :param creator:
        '''
        Room.__init__(self, server, room_name)
        self.creator = creator  # 群主

    def add(self, session):
        '''
        添加新用户进群
        并将新用户进入的消息 广播给群内其他人
        :param session:
        :return:
        '''
        self.sessions.append(session)
        broad_dict = dict(type='person_in', group_name=self.room_name, user_name=session.user_name)
        broad_json = json.dumps(broad_dict, ensure_ascii=False)
        self.broadcast(session, broad_json)

    def do_desc_group(self, session, cmd_dict):
        '''
        描述群，返回的serverResponse是字典
        :param session:
        :param cmd_dict:
        :return:
        '''
        info_dict = dict(creator=self.creator, group_name=self.room_name, members=list())
        for user_session in self.sessions:
            # 取出所有用户名
            info_dict['members'].append(user_session.user_name)
        session.push((ServerResponse('Succeed.', status=True, info=info_dict) + '\r\n').encode('utf-8'))

    def do_leave_group(self, session, cmd_dict):
        '''
        离开群，返回大厅
        广播告诉其他人自己离开了
        :param session:
        :param cmd_dict:
        :return:
        '''
        self.sessions.remove(session)  # 当前房间中删除
        broad_dict = dict(type='person_out', group_name=self.room_name, user_name=session.user_name)
        broad_json = json.dumps(broad_dict, ensure_ascii=False)
        self.broadcast(session, broad_json)
        session.enter(self.server.hall)  # 返回大厅
        session.push((ServerResponse('Succeed.') + '\r\n').encode('utf-8'))

    def do_group_message(self, session, group_msg_dict):
        '''
        {'type': 'group_message',
        'msg': '在群内说话',
        'usr_name': 'lrx',
        'group_name': 'group1',
        'timestamp': 1530000000}
        :param session:
        :param group_msg_dict:
        :return:
        '''
        broad_dict = dict(type='person_speak', group_name=self.room_name, user_name=session.user_name,
                          message=group_msg_dict['msg'])
        broad_json = json.dumps(broad_dict, ensure_ascii=False)
        self.broadcast(session, broad_json)
        session.push((ServerResponse('Succeed.') + '\r\n').encode('utf-8'))


class SingleRoom(Room):
    '''
    一对一聊天
    :param Room:
    :return:
    '''
    pass
