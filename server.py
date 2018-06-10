# coding: utf-8
import socket
import threading
import json
import struct
import time

GLOBAL_USER_ID = 0
GLOBAL_ROOM_ID = 0

avai_port = [1, 1, 1, 1, 1] #分别对应端口8001~8005，这些端口用于文件的传输
base_port = 8000
def findAvaiPort():
    # todo 需要锁同步
    port_num = len(avai_port)
    port = -1
    while port == -1:
        for i in range(0, port_num):
            if avai_port[i] == 1:
                port = base_port + i + 1
                avai_port[i] = 0
                return port
        time.sleep(0.5)
    print('找到了可用的port=',port)
    return port

def releasePort(port):
    # todo 需要锁同步
    avai_port[port-base_port-1] = 1


class User:
    def __init__(self):
        global GLOBAL_USER_ID
        self.name = '用户'+str(GLOBAL_USER_ID)
        self.id = GLOBAL_USER_ID
        self.session = None
        self.friends = {}
        GLOBAL_USER_ID += 1

    def recv(self):
        print('等候接收')
        pre_data = self.session.recv(50)
        pre_data = json.loads(pre_data.decode('utf-8').strip('\00'))
        if pre_data['type'] == 'len':
            data_len = pre_data['len']
            print('数据长度为%d'%data_len)
            recv_data = self.session.recv(data_len).decode('utf-8')
            return json.loads(recv_data)

    def process(self, session, all_users, all_rooms):
        print('新用户：%d'%(GLOBAL_USER_ID-1))
        self.session = session
        #0. 第0步把系统分配的name和id号发给用户（name是次要的，主要是id号）
        self.initUser()
        print('发送name和id成功')

        #1. 第一步就是把该用户加入到公共房间.
        self.enterRoom(all_rooms[0])
        print('给新用户发了公共房间的信息了')

        #2. 第二步就是让用户和之前所有的用户成为好友
        for i in range(0, GLOBAL_USER_ID-1):
            room = Room(single=True)
            all_rooms[GLOBAL_ROOM_ID-1] = room
            room.member = {self.id: self.name, all_users[i].id: all_users[i].name}
            self.enterRoom(room)
            all_users[i].enterRoom(room)

        #3. 进入和用户交互的无线循环

        while True:
            try:
                recv_data = self.recv()
            except:
                print('接收出错了或者用户退出了')
                return
            data_type = recv_data['type']
            print(recv_data)
            if data_type == 'roomMessage':
                room = all_rooms[recv_data['room_id']]
                self.sendMessageToRoom(recv_data, room)
            elif data_type == 'fileShare':
                port = findAvaiPort()
                send_data = {'type': 'fileShare', 'port': port}
                send_data = json.dumps(send_data).encode('utf-8')
                self.send(send_data)
                t1 = threading.Thread(target=self.processShareFile, args=(host, port, all_rooms[recv_data['room_id']]))
                t1.start()

    def processShareFile(self, host, port, room):
        # 为接收、发送文件开辟的线程
        print('开始接收文件，port=', port)
        fsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        fsock.bind((host, port))
        fsock.listen(1)
        csock, caddr = fsock.accept()

        pre_data_len = struct.calcsize('128sl')
        pre_data = csock.recv(pre_data_len)
        file_name, file_size = struct.unpack('128sl', pre_data)
        file_name = file_name.decode('utf-8').strip('\00')

        recv_len = 0
        recv_data = b''
        while recv_len < file_size:
            if file_size - recv_len > 1024:
                recv_data += csock.recv(1024)
                recv_len += 1024
            else:
                recv_data += csock.recv(file_size - recv_len)
                recv_len = file_size
        room.files[file_name] = recv_data   # 将文件保存在room中，以备之后给其他用户传送

        send_data = {'type':'remindFile'}
        send_data['user_id'] = self.id
        send_data['user_name'] = self.name
        send_data['file_name'] = file_name
        send_data['room_id'] = room.id
        send_data = json.dumps(send_data).encode('utf-8')
        for user_id in room.member:
            if user_id != self.id:
                if all_users[user_id].send(send_data) is False:
                    print('错误：当向用户<%s>发送文件提醒时'%all_users[user_id].name)
        csock.close()
        releasePort(port) #释放port



    def sendMessageToRoom(self, data, room):
        data['user_id'] = self.id           #让其他人知道，该信息是谁发的
        data['user_name'] = self.name
        data = json.dumps(data).encode('utf-8')
        for user_id in room.member:
            if user_id != self.id:
                if all_users[user_id].send(data) is False:
                    print("群聊错误：用户<%s>在向用户<%s>发送消息时出错"%(self.name, all_users[user_id].name))


    def enterRoom(self, room):
        # 向用户发送关于room的信息，让其加入该room
        send_data = {}
        send_data['type'] = 'selfEnterRoom'
        send_data['single'] = room.single
        send_data['room_name'] = room.name
        send_data['room_id'] = room.id
        send_data['owner'] = room.owner
        send_data['member'] = room.member
        send_data = json.dumps(send_data).encode('utf-8')
        if self.send(send_data) is True and room.single is False:
            room.member[self.id] = self.name
            # 向房间内的其他人通知有人来了
            send_data = json.loads(send_data.decode('utf-8'))
            send_data['type'] = 'otherEnterRoom'
            send_data['user_id'] = self.id
            send_data['user_name'] = self.name
            send_data = json.dumps(send_data).encode('utf-8')
            for user_id in room.member:
                if user_id != self.id:
                    if all_users[user_id].send(send_data) is False:
                        print("错误：向用户<%s>通知用户<%s>加入到房间<%s>时出错"%(all_users[user_id].name, self.name, room.name))

        elif room.single is False:
            print('进房错误：当把用户<%s>加入到房间<%s>时'%(self.name, room.name))

    def initUser(self):
        send_data = {}
        send_data['type'] = 'initUser'
        send_data['name'] = self.name
        send_data['id'] = self.id
        send_data = json.dumps(send_data).encode('utf-8')
        if self.send(send_data) is False:
            print("初始错误：用户<%s>刚进来时给他发送一个名字都失败了吗！"%(self.name))


    def send(self, send_data):
        try:
            pre_data = {'type': 'len'}
            pre_data['len'] = len(send_data)
            pre_data = json.dumps(pre_data).encode('utf-8')
            pre_data = struct.pack('50s', pre_data)
            self.session.send(pre_data)
            self.session.sendall(send_data)
            return True
        except:
            return False

class Room:
    def __init__(self, single):
        global GLOBAL_ROOM_ID
        self.name = 'room'+str(GLOBAL_ROOM_ID)
        self.id = GLOBAL_ROOM_ID
        self.owner = None
        self.single = single     #True则为私聊
        self.member = {}    # user's id: user's session
        self.files = {}
        GLOBAL_ROOM_ID += 1

all_users = {}  # user'id:   User
all_rooms = {}  # room's id: Room
publicRoom = Room(single=False) #第一个群聊为公共群聊，用户一上线，就加入到他里面了
publicRoom.name = '公众聊天室'
all_rooms[GLOBAL_ROOM_ID-1] = publicRoom

host = '0.0.0.0'
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.bind((host, base_port))
sock.listen(10)

while True:
    print('等候下一个用户')
    session, addr = sock.accept()
    print('连接到了用户,addr=', addr)
    user = User()
    all_users[GLOBAL_USER_ID-1] = user
    print('新用户的id为%d'%(GLOBAL_USER_ID-1))
    t = threading.Thread(target=user.process, args=(session, all_users, all_rooms))
    print('新用户的线程在执行...')
    t.start()







