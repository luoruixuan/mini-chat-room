# -*- coding: utf-8 -*-

import json
import traceback
import datetime
import DataBaseInterface
from project_logger import logger
from secure_transmission import *
import threading
import socket
import struct


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
                # 用户请求传送文件
                method = getattr(self, 'do_file_message', None)
                method(session, cmd_dict)
            elif cmd_dict['type'] == 'download_file':
                #用户请求下载文件
                method = getattr(self, 'do_download_file', None)
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

    def do_init_AES_Key(self, session, cmd_dict):
        '''
        初始化AES密钥
        # 接收AES密钥
        {'type': 'init',
         'msg': 'AESKey',
         'Key': ''
        }
        :param session:
        :param cmd_dict:
        :return:
        '''
        if cmd_dict['msg'] == 'AESKey':
            session.AESinstance.key = str(session.RSAinstance.RSADecrypt(cmd_dict['Key']), encoding='utf-8')
            session.SecurityPush((ServerResponse(msg='AC_AESKey') + '\r\n').encode('utf-8'))
            session.AESKey_is_init = True

    def do_register(self, session, cmd_dict):
        '''
        注册用户
        :param session:
        :param cmd_dict:
        :return:
        '''
        usr_name = cmd_dict['usr_name']
        password = cmd_dict['password']
        for up_tuple in self.server.all_users:
            if usr_name == up_tuple[0]:
                session.SecurityPush((ServerResponse('Usr_name exist.', False) + '\r\n').encode('utf-8'))
                return
        # 用户名不冲突
        new_tuple = (usr_name, password)
        self.server.all_users.append(new_tuple)
        # 数据库中加入新用户
        user_query = DataBaseInterface.UserOperations()
        user_query.add(usr_name, password)
        session.SecurityPush((ServerResponse('Succeed.') + '\r\n').encode('utf-8'))

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
        else:
            if name in self.server.active_users:
                # 这里是阻止同一个用户重复登录，因此检查用的是active_users
                # self.server.active_users[name].do_logout(self.server.active_users[name], dict)
                # session.SecurityPush((ServerResponse('usr already login', False) + '\r\n').encode('utf-8'))
                # 挤掉上次的登陆session
                last_session = self.server.active_users[name]
                del self.server.active_users[name]  # 服务器活跃用户列表中删除
                for entered_room in last_session.entered_rooms.values():
                    entered_room.remove_session(last_session)
                last_session.handle_close()
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
        group_query.CreateGroup(group_name)  # 这个函数已测试可用

        session.SecurityPush((ServerResponse('Succeed.') + '\r\n').encode('utf-8'))

    def do_enter_group(self, session, cmd_dict):
        '''
        进入一个群
        这个有什么数据库操作吗
        是否还允许用户直接进入某一个群？
        Okay 这个函数没了
        :param session:
        :param cmd_dict:
        :return:
        '''
        session.SecurityPush((ServerResponse('not implemented', False) + '\r\n').encode('utf-8'))
        return
        group_name = cmd_dict['group_name']
        if group_name not in self.server.group_rooms:
            session.SecurityPush((ServerResponse('group not exist', False) + '\r\n').encode('utf-8'))
            return
        session.enter(self.server.group_rooms[group_name])

        # 数据库操作应该是，把某个用户加到某个群里
        # Todo 这个操作不应该有了
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

    def do_add_friend(self, session, cmd_dict):
        '''
        添加好友
        :param session:
        :param cmd_dict:
        :return:
        '''
        # 在数据库中记录一条好友记录（id1, id2, 0, verification_message）
        # 确认的好友记录变为(id1, id2, 1, verification_message)
        # 拒绝的好友记录变为(id1, id2, -1, verification_message)
        # 表示id1向id2的请求
        usr_name = cmd_dict['usr_name']
        friend_name = cmd_dict['friend_name']
        verification_message = cmd_dict['verification_message']
        friend_query = DataBaseInterface.UserFriends(usr_name)
        friend_query.add(friend_name, verification_message)
        session.SecurityPush((ServerResponse('Succeed.') + '\r\n').encode('utf-8'))

    def do_get_verification_message(self, session, cmd_dict):
        '''
        查看收到的好友请求记录
        :param session:
        :param cmd_dict:
        :return:
        '''
        usr_name = cmd_dict['usr_name']
        friend_query = DataBaseInterface.UserFriends(usr_name)
        # {'wy':'hello', 'ly':'hi', 'qwt':'Hi'}
        info_dict = friend_query.query_request().copy()
        session.SecurityPush((ServerResponse('Succeed.', info=info_dict) + '\r\n').encode('utf-8'))
        pass

    def do_add_friend_response(self, session, cmd_dict):
        '''
        接受或拒绝请求
        :param session:
        :param cmd_dict:
        :return:
        '''
        usr_name = cmd_dict['usr_name']
        friend_name = cmd_dict['friend_name']
        accept = cmd_dict['accept']
        if accept:
            friend_query = DataBaseInterface.UserFriends(usr_name)
            friend_query.accept(friend_name)
            # 成为好友之后自动创建名为 “&a&b” 的房间，并把俩人拉进去
            if usr_name < friend_name:
                group_name = '&' + usr_name + '&' + friend_name
                self.server.group_rooms[group_name] = GroupRoom(self.server, group_name, usr_name)  # 创建群
                friend_session = self.server.active_users.get(friend_name, None)
                session.enter(self.server.group_rooms[group_name])
                if friend_session != None:
                    friend_session.enter(self.server.group_rooms[group_name])
                broad_dict = dict(type='usr_invited', group_name=group_name,
                                  msg='You are invited into ' + group_name)
                broad_json = json.dumps(broad_dict, ensure_ascii=False)
                session.SecurityPush((broad_json + '\r\n').encode('utf-8'))
                if friend_session != None:
                    friend_session.SecurityPush((broad_json + '\r\n').encode('utf-8'))
                if not friend_name in self.server.group_rooms[group_name].users:
                    self.server.group_rooms[group_name].users.append(friend_name)
                group_query = DataBaseInterface.ChatGroup(usr_name)
                group_query.CreateGroup(group_name)
                group_query.addGroupMem(friend_name)
            else:
                group_name = '&' + friend_name + '&' + usr_name
                self.server.group_rooms[group_name] = GroupRoom(self.server, group_name, friend_name)  # 创建群
                friend_session = self.server.active_users.get(friend_name, None)
                session.enter(self.server.group_rooms[group_name])
                if friend_session != None:
                    friend_session.enter(self.server.group_rooms[group_name])
                broad_dict = dict(type='usr_invited', group_name=group_name,
                                  msg='You are invited into ' + group_name)
                broad_json = json.dumps(broad_dict, ensure_ascii=False)
                session.SecurityPush((broad_json + '\r\n').encode('utf-8'))
                if friend_session != None:
                    friend_session.SecurityPush((broad_json + '\r\n').encode('utf-8'))
                if not friend_name in self.server.group_rooms[group_name].users:
                    self.server.group_rooms[group_name].users.append(friend_name)
                group_query = DataBaseInterface.ChatGroup(friend_name)
                group_query.CreateGroup(group_name)
                group_query.addGroupMem(usr_name)
            session.SecurityPush((ServerResponse('Succeed.') + '\r\n').encode('utf-8'))
        else:
            friend_query = DataBaseInterface.UserFriends(usr_name)
            friend_query.reject(friend_name)
            session.SecurityPush((ServerResponse('Succeed.') + '\r\n').encode('utf-8'))

    def do_get_group_list(self, session, cmd_dict):
        '''
        查询用户所在群列表
        :param session:
        :param cmd_dict:
        :return:
        '''
        usr_name = cmd_dict['usr_name']
        g_list = list(self.server.active_users[usr_name].entered_rooms.keys())
        g_list.remove('Hall')
        session.SecurityPush((ServerResponse('Succeed.', info=g_list) + '\r\n').encode('utf-8'))

    def do_get_friend_list(self, session, cmd_dict):
        '''
        查询用户好友列表
        :param session:
        :param cmd_dict:
        :return:
        '''
        usr_name = cmd_dict['usr_name']
        friend_query = DataBaseInterface.UserFriends(usr_name)
        friend_list = []
        friend_query.queryFriendList(friend_list)
        session.SecurityPush((ServerResponse('Succeed.', info=friend_list) + '\r\n').encode('utf-8'))


class GroupRoom(Room):
    '''
    群
    本层支持的命令:
    desc_group
    remove_person
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
        self.files = {} # 文件名：文件内容（内容为二进制）

    def add_session(self, session):
        '''
        添加一个新的session
        相当于一个新的群内用户上线
        :param session:
        :return:
        '''
        self.sessions.append(session)
        if not session.usr_name in self.users:
            self.users.append(session.usr_name)

    def do_desc_group(self, session, cmd_dict):
        '''
        描述群，返回的serverResponse是字典
        :param session:
        :param cmd_dict:
        :return:
        '''
        info_dict = dict(creator=self.creator, group_name=self.room_name, members=list(),
                         files=list(), history=list())
        # 获取某个群内的所有用户名
        group_query = DataBaseInterface.ChatGroup(session.usr_name)
        info_dict['members'] = self.users.copy()
        # 获取某个群内的文件
        # info_dict['files'] = group_query.query_files()
        # 获取历史消息
        message_query = DataBaseInterface.GroupMessages(session.usr_name, self.room_name)
        info_dict['history'] = message_query.get_history(self.room_name).copy()

        session.SecurityPush((ServerResponse('Succeed.', status=True, info=info_dict) + '\r\n').encode('utf-8'))

    def do_remove_person(self, session, cmd_dict):
        '''
        删除群内的人，有三种情况
        1、群主删除自己，则群解散
        2、群主删除一个人
        3、自己删除自己，则退出该群
        :param session:
        :param cmd_dict:
        :return:
        '''
        name = cmd_dict['usr_name']
        friend_name = cmd_dict['friend_name']
        if name == self.creator and name == friend_name:
            # 群主删除自己
            broad_dict = dict(type='usr_removed', group_name=self.room_name,
                              msg='You are removed from ' + self.room_name)
            # 群解散，广播告知所有在这个群内的session
            broad_json = json.dumps(broad_dict, ensure_ascii=False)
            self.broadcast(session, broad_json)
            session.SecurityPush((broad_json + '\r\n').encode('utf-8'))

            # 这个群被删除了，对每个session都去掉记录，对服务器去掉记录
            # 或者说是消除内存中的记录
            for user_session in self.sessions:
                del user_session.entered_rooms[self.room_name]
            del self.server.group_rooms[self.room_name]

            # 数据库操作，彻底解散群，消除数据库中的记录
            group_query = DataBaseInterface.ChatGroup(name)
            group_query.OpenGroup(self.room_name)
            group_query.removeMem(name)
            session.SecurityPush((ServerResponse('Succeed.') + '\r\n').encode('utf-8'))
        elif name == self.creator and name != friend_name:
            try:
                friend_session = self.server.active_users[friend_name]
            except KeyError as err:
                friend_session = None
            # 群主踢人
            broad_dict = dict(type='usr_removed', group_name=self.room_name,
                              msg='You are removed from ' + self.room_name)
            # 只向被踢的人发
            broad_json = json.dumps(broad_dict, ensure_ascii=False)
            if friend_session is not None:
                friend_session.SecurityPush((broad_json + '\r\n').encode('utf-8'))
            # 告诉别人这个人被踢了
            broad_dict = dict(type='person_out', group_name=self.room_name, usr_name=friend_name)
            broad_json = json.dumps(broad_dict, ensure_ascii=False)
            self.broadcast(friend_session, broad_json)
            # 删除内存记录
            if friend_session is not None:
                del friend_session.entered_rooms[self.room_name]
                self.remove_session(friend_session)
            self.users.remove(friend_name)
            # 删除数据库记录
            group_query = DataBaseInterface.ChatGroup(name)
            group_query.OpenGroup(self.room_name)
            group_query.removeMem(friend_name)
            session.SecurityPush((ServerResponse('Succeed.') + '\r\n').encode('utf-8'))
        elif name != self.creator and name == friend_name:
            # 删除自己
            broad_dict = dict(type='usr_removed', group_name=self.room_name,
                              msg='You are removed from ' + self.room_name)
            broad_json = json.dumps(broad_dict, ensure_ascii=False)
            session.SecurityPush((broad_json + '\r\n').encode('utf-8'))
            broad_dict = dict(type='person_out', group_name=self.room_name, usr_name=name)
            broad_json = json.dumps(broad_dict, ensure_ascii=False)
            self.broadcast(session, broad_json)
            del session.entered_rooms[self.room_name]
            self.remove_session(session)
            self.users.remove(name)
            group_query = DataBaseInterface.ChatGroup(name)
            group_query.OpenGroup(self.room_name)
            group_query.removeMem(name)
            session.SecurityPush((ServerResponse('Succeed.') + '\r\n').encode('utf-8'))
        else:
            # 删除失败
            session.SecurityPush((ServerResponse('remove fail', False) + '\r\n').encode('utf-8'))

    def do_leave_group(self, session, cmd_dict):
        '''
        某一个用户离开某一个群
        分两种情况，是群主则直接解散该群；不是群主则退出该群
        :param session:
        :param cmd_dict:
        :return:
        '''
        session.SecurityPush((ServerResponse('not implemented', False) + '\r\n').encode('utf-8'))
        return
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
        server_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        broad_dict = dict(type='person_speak', group_name=self.room_name, usr_name=session.usr_name,
                          message=group_msg_dict['msg'], date_time=server_time)
        broad_json = json.dumps(broad_dict, ensure_ascii=False)
        self.broadcast(session, broad_json)
        # 记录进数据库里
        message_query = DataBaseInterface.GroupMessages(session.usr_name, self.room_name)
        message_query.addMessage(broad_dict['usr_name'], broad_dict['message'], broad_dict['date_time'])

        session.SecurityPush((ServerResponse('Succeed.') + '\r\n').encode('utf-8'))

    # def do_file_message(self, session, file_message_dict):
    #     server_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    #     broad_dict = dict(type='person_share_file', group_name=self.room_name,
    #                       usr_name=session.usr_name, file_name=file_message_dict['file_name'],
    #                       file_content=file_message_dict['file_content'],
    #                       date_time=server_time)
    #     broad_json = json.dumps(broad_dict, ensure_ascii=False)
    #     self.broadcast(session, broad_json)
    #     session.SecurityPush((ServerResponse('Succeed.') + '\r\n').encode('utf-8'))

    def do_file_message(self, session, file_message_dict):
        # 功能：向客户端发送端口信息
        print('处理来自用户分享的文件')
        server_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        port = 8003
        file_name = file_message_dict['file_name']
        usr_name = session.usr_name

        host = '0.0.0.0'
        send_data = dict(type = 'server_response', msg = 'for share', host = host, port = port)
        send_data = json.dumps(send_data)
        send_data = (send_data + '\r\n').encode('utf-8')
        session.SecurityPush(send_data)
        def process_recv_file(room):
            print('服务器进入接收文件的线程了')
            sock, csock = None, None
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.bind(('0.0.0.0', port))
            sock.listen(1)
            print('建立套接字(%s,%d)成功' % (host, port))
            csock, caddr = sock.accept()
            print('客户机连接到了')

            pre_data_len = struct.calcsize('128sl')
            pre_data = csock.recv(pre_data_len)
            file_name, file_len = struct.unpack('128sl', pre_data)
            file_name = file_name.decode('utf-8').strip('\00')

            print('将接收长为%d的文件%s'%(file_len, file_name))
            # 接收文件
            buf_len = int(file_len/100)
            buf_len = max(100, buf_len)
            buf_len = min(300000, buf_len)
            recv_data = b''
            recv_len = 0
            while recv_len != file_len:
                if recv_len + buf_len < recv_len:
                    recv_data += csock.recv(buf_len)
                    recv_len = len(recv_data)
                else:
                    recv_data += csock.recv(file_len - recv_len)
                    recv_len = len(recv_data)
                print('当前接收长度：', recv_len)
            print('服务器接受文件成功')

            if csock is not None:
                csock.close()
            if sock is not None:
                sock.close()

            room.files[file_name] = recv_data     # 房间存储接收到的数据

            # 向room内的其他用户发送文件提醒的消息
            broad_data = dict(type = 'person_share_file', usr_name = usr_name,
                             group_name = room.room_name, file_name = file_name,
                             data_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
            broad_data = json.dumps(broad_data)
            room.broadcast(session, broad_data)

            print('用户%s的文件%s接收完毕' % (usr_name, file_name))

        t = threading.Thread(target=process_recv_file, args=(self,))
        t.start()

    def do_download_file(self, session, message_dict):
        # 向需要下载文件的用户传输文件
        print('处理来自用户的文件请求')
        server_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        port = 8003
        file_name = message_dict['file_name']
        usr_name = session.usr_name

        host = '0.0.0.0'
        send_data = dict(type = 'server_response', msg = 'for download', host = host, port = port)
        send_data = json.dumps(send_data)
        send_data = (send_data + '\r\n').encode('utf-8')
        session.SecurityPush(send_data)

        def process_send_file(room, file_name):
            print('服务器进入发送文件的线程了')
            sock, csock = None, None
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.bind(('0.0.0.0', port))
            sock.listen(1)
            print('建立套接字(%s,%d)成功' % (host, port))
            csock, caddr = sock.accept()
            print('客户机连接到了')

            file_data = room.files[file_name]
            file_len = len(file_data)

            pre_data = struct.pack('128sl', file_name.encode('utf-8'), file_len)
            csock.sendall(pre_data)

            print('将发送长为%d的文件%s'%(file_len, file_name))
            # 发送文件
            # 先设置缓冲区的大小，大的缓冲区对于加快大文件的传输很有用
            buf_len = int(file_len/100)
            buf_len = max(100, buf_len)
            buf_len = min(300000, buf_len)
            send_len = 0
            while send_len != file_len:
                if send_len + buf_len < file_len:
                    csock.sendall(file_data[send_len:send_len+buf_len])
                    send_len += buf_len
                else:
                    csock.sendall(file_data[send_len:])
                    send_len = file_len
                print('当前发送长度：', send_len)
            print('服务器发送文件成功')

            if csock is not None:
                csock.close()
            if sock is not None:
                sock.close()

            print('向用户%s的送文件%s完成' % (usr_name, file_name))

        t = threading.Thread(target=process_send_file, args=(self,file_name))
        t.start()

    def do_invite_friend(self, session, cmd_dict):
        '''
        拉好友进群，如果在线，就将对方的session拉进来
        如果不在线，就只加到数据库里
        :param session:
        :param cmd_dict:
        :return:
        '''
        usr_name = cmd_dict['usr_name']
        friend_name = cmd_dict['friend_name']
        group_name = cmd_dict['group_name']
        friend_session = self.server.active_users.get(friend_name, None)
        if friend_session != None:
            friend_session.enter(self)
        # 告知所有群内用户 person_in
        broad_dict = dict(type='person_in', group_name=self.room_name, usr_name=friend_name)
        broad_json = json.dumps(broad_dict, ensure_ascii=False)
        self.broadcast(friend_session, broad_json)
        if friend_session != None:
            # 给被邀请人发一个usr_invited
            broad_dict = dict(type='usr_invited', group_name=self.room_name,
                              msg='You are invited into ' + self.room_name)
            broad_json = json.dumps(broad_dict, ensure_ascii=False)
            friend_session.SecurityPush((broad_json + '\r\n').encode('utf-8'))

        # 修改数据库
        if not friend_name in self.users:
            self.users.append(friend_name)
        group_query = DataBaseInterface.ChatGroup(usr_name)
        group_query.OpenGroup(self.room_name)
        group_query.addGroupMem(friend_name)
        session.SecurityPush((ServerResponse('Succeed.') + '\r\n').encode('utf-8'))
