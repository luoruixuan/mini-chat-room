# -*- coding: utf-8 -*-

# todo
# 1、所有的时间戳都没考虑

import json
import traceback
import DataBaseInterface
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
        session.SecurityPush((ServerResponse('bad command', False) + '\r\n').encode('utf-8'))  # 这里用push，是async_chat的方式

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
                except EndSession as end:
                    # 发现了是结束会话，抛给上层
                    raise EndSession
                except Exception as err:
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
            elif cmd_dict['type'] == 'file_message':
                method = getattr(self, 'do_file_message', None)

                method(session, cmd_dict)

                # raise BadCmd
            # by lanying
            elif cmd_dict['type'] == 'init':
                method = getattr(self, 'do_init_AES_Key', None)
                try:
                    method(session, cmd_dict)
                except:
                    raise BadCmd
            # by lanying

            else:
                raise BadCmd
        except Exception as err:
            if isinstance(err, EndSession):
                raise EndSession  # 这个不能在这被捕获
                return
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
        为了支持离线聊天，需要保存当前房间内有哪些用户（不一定在线）
        :param server:
        :param room_name:
        '''
        self.sessions = []
        self.users = []  # 这个是为了保存有哪些用户的，存的是用户名['lrx', 'wy']
        self.server = server
        self.room_name = room_name

    def add_session(self, session):
        self.sessions.append(session)

    def remove_session(self, session):
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
                i.SecurityPush((line + '\r\n').encode('utf-8'))

    def do_logout(self, session, line):
        raise EndSession


class Hall(Room):
    '''
    大厅，处理用户登入登出等
    本层支持的命令:
    login
    logout
    change_password
    create_group
    create_single
    enter_group
    '''

    def add_session(self, session):
        '''
        新用户的会话出现，加到大厅里
        :param session:
        :return:
        '''
        self.sessions.append(session)
        if session.usr_name == '':
            # 空用户名表示一个未注册的用户
            # session.SecurityPush((ServerResponse('please login') + '\r\n').encode('utf-8'))
            pass
        else:
            # 由于可以同时在多个房间里，因此这句没用了
            session.SecurityPush((ServerResponse('back to hall') + '\r\n').encode('utf-8'))

    def do_login(self, session, cmd_dict):
        '''
        处理用户登陆命令

        检查服务器的用户列表中是否有这个用户，并且密码是否匹配（注册放在另一个地方）
        :param session:
        :param cmd_dict:
        :return:
        '''
        name = cmd_dict['usr_name']
        password = cmd_dict['password']
        login_timestamp = cmd_dict['timestamp']
        # 3、用户登入时，根据数据库，初始化该用户所在的房间列表，并发最近消息给该用户（todo，传一个
        # 时间戳在登陆时，发这个时间之后的消息）

        if not name:
            session.SecurityPush((ServerResponse('usr_name empty', False) + '\r\n').encode('utf-8'))
        elif name in self.server.active_users:
            # 这里是阻止同一个用户重复登录，因此检查用的是active_users
            session.SecurityPush((ServerResponse('usr_name exist', False) + '\r\n').encode('utf-8'))
        else:
            # 去服务器用户列表中检查
            matched = False
            for up_tuple in self.server.all_users:
                if name == up_tuple[0] and password == up_tuple[1]:
                    matched = True
                    break
                elif name == up_tuple[0] and password != up_tuple[1]:
                    session.SecurityPush((ServerResponse('Password error.', False) + '\r\n').encode('utf-8'))
                    return
            if not matched:
                session.SecurityPush((ServerResponse('User not exist.', False) + '\r\n').encode('utf-8'))
                return
            # 只有在 server.all_users中找到了用户并匹配了密码，才登录成功
            session.usr_name = name
            self.server.active_users[session.usr_name] = session  # 服务器端保存新活跃用户的名称，映射到它的会话
            # 初始化这个用户所在的房间列表(即群) session.entered_rooms
            group_query = DataBaseInterface.ChatGroup(username=name)
            room_names = []
            res = group_query.queryChatGroupList(room_names)
            for room_name in room_names:
                session.enter(self.server.group_rooms[room_name])
                # enter里调用的是 room.add_session，所以不应该用 person_in 广播了，得处理一下
                # 也就是说，一个用户在不在一个群里，和它的session打不打开应该没关系
                # 房间内都应该能看到这个用户，但不一定有这个用户的session

            session.SecurityPush((ServerResponse('Succeed.') + '\r\n').encode('utf-8'))

    def do_logout(self, session, cmd_dict):
        '''
        处理用户登出
        :param session:
        :param cmd_dict:
        :return:
        '''
        del self.server.active_users[session.usr_name]  # 服务器活跃用户列表中删除
        # 所在每个房间的sessions中删除，包括了大厅和所有所在的群
        for entered_room in session.entered_rooms.values():
            entered_room.remove_session(session)
        session.SecurityPush((ServerResponse('Succeed.') + '\r\n').encode('utf-8'))
        raise EndSession  # 抛出结束会话异常

    def do_change_password(self, session, cmd_dict):
        '''
        修改密码
        :param session:
        :param cmd_dict:
        :return:
        '''
        # 这个操作将修改数据库中存储的密码，而服务器内存中保存的密码也得修改一份
        # 原则：先改内存后改数据库？尽量还是原子性的，防止不一致吧
        usr_name = cmd_dict['usr_name']
        old_password = cmd_dict['old_password']
        new_password = cmd_dict['new_password']
        # 只能修改自己的密码，同时确定了用户是已存在的用户
        if usr_name != session.usr_name:
            session.SecurityPush((ServerResponse('No authority.', False) + '\r\n').encode('utf-8'))
            return
        # 去服务器用户列表中检查
        match_tuple = ()
        for up_tuple in self.server.all_users:
            if usr_name == up_tuple[0] and old_password == up_tuple[1]:
                match_tuple = up_tuple
                # 匹配到了，那么更换成新密码
                break
            elif usr_name == up_tuple[0] and old_password != up_tuple[1]:
                session.SecurityPush((ServerResponse('OldPassword error.', False) + '\r\n').encode('utf-8'))
                return
        # match_tuple 不会是()，否则前面就会退出
        self.server.all_users.remove(match_tuple)
        new_tuple = (usr_name, new_password)
        self.server.all_users.append(new_tuple)
        # 服务器是单线程的，还需要更新数据库中的(用户名，密码)对
        user_query = DataBaseInterface.UserOperations()
        res = user_query.change_password(usr_name, new_password)
        if res == -1:
            session.SecurityPush((ServerResponse('Modify db Fail.', False) + '\r\n').encode('utf-8'))
            # 这个错误，应该不会出现。
        elif res == 0:
            session.SecurityPush((ServerResponse('Succeed.') + '\r\n').encode('utf-8'))

    def do_create_group(self, session, cmd_dict):
        '''
        创建一个群，并进入（成为群主）
        加上数据库操作
        :param session:
        :param cmd_dict:
        :return:
        '''
        group_name = cmd_dict['group_name']
        if group_name in self.server.group_rooms:
            session.SecurityPush((ServerResponse('group exist', False) + '\r\n').encode('utf-8'))
            return
        self.server.group_rooms[group_name] = GroupRoom(self.server, group_name, session.usr_name)  # 创建群
        session.enter(self.server.group_rooms[group_name])
        # 在数据库内添加这个群，并把群主加入这个群（已封装）
        group_query = DataBaseInterface.ChatGroup(session.usr_name)
        group_query.CreateGroup(group_name) # 这个函数已测试可用

        session.SecurityPush((ServerResponse('Succeed.') + '\r\n').encode('utf-8'))

    def do_enter_group(self, session, cmd_dict):
        '''
        进入一个群
        这个有什么数据库操作吗
        是否还允许用户直接进入某一个群？
        :param session:
        :param cmd_dict:
        :return:
        '''
        group_name = cmd_dict['group_name']
        if group_name not in self.server.group_rooms:
            session.SecurityPush((ServerResponse('group not exist', False) + '\r\n').encode('utf-8'))
            return
        session.enter(self.server.group_rooms[group_name])
        session.SecurityPush((ServerResponse('Succeed.') + '\r\n').encode('utf-8'))

        # 告知群内其他人，这个在GroupRoom.add_session()方法内完成

    def do_enter_single(self, session, cmd_dict):
        '''
        建立一对一聊天
        :param session:
        :param cmd_dict:
        :return:
        '''
        session.SecurityPush((ServerResponse('not implemented', False) + '\r\n').encode('utf-8'))
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

    def add_session(self, session):
        '''
        添加新用户进群
        并将新用户进入的消息 广播给群内其他人
        :param session:
        :return:
        '''
        self.sessions.append(session)
        broad_dict = dict(type='person_in', group_name=self.room_name, usr_name=session.usr_name)
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
            info_dict['members'].append(user_session.usr_name)
        session.SecurityPush((ServerResponse('Succeed.', status=True, info=info_dict) + '\r\n').encode('utf-8'))

    def do_leave_group(self, session, cmd_dict):
        '''
        离开群，返回大厅
        广播告诉其他人自己离开了
        :param session:
        :param cmd_dict:
        :return:
        '''
        self.sessions.remove(session)  # 当前房间中删除
        broad_dict = dict(type='person_out', group_name=self.room_name, usr_name=session.usr_name)
        broad_json = json.dumps(broad_dict, ensure_ascii=False)
        self.broadcast(session, broad_json)
        session.enter(self.server.hall)  # 返回大厅
        session.SecurityPush((ServerResponse('Succeed.') + '\r\n').encode('utf-8'))

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
        broad_dict = dict(type='person_speak', group_name=self.room_name, usr_name=session.usr_name,
                          message=group_msg_dict['msg'])
        broad_json = json.dumps(broad_dict, ensure_ascii=False)
        self.broadcast(session, broad_json)
        session.SecurityPush((ServerResponse('Succeed.') + '\r\n').encode('utf-8'))

    def do_file_message(self, session, file_message_dict):
        broad_dict = dict(type='person_share_file', group_name=self.room_name,
                          usr_name=session.usr_name, file_name=file_message_dict['file_name'],
                          file_content=file_message_dict['file_content'])
        broad_json = json.dumps(broad_dict, ensure_ascii=False)
        self.broadcast(session, broad_json)
        session.SecurityPush((ServerResponse('Succeed.') + '\r\n').encode('utf-8'))


class SingleRoom(Room):
    '''
    一对一聊天
    :param Room:
    :return:
    '''
    pass
