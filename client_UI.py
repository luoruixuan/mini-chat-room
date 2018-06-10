# coding: utf-8
import tkinter as tk
from tkinter import filedialog, font

import socket
import threading
import json
import struct
import os

class Room:
    def __init__(self, single):
        self.name = None
        self.id = None
        self.single = single
        self.owner = None
        self.member = {}    # user's id: user's name
        self.history = []   #存储该房间的历史信息
        self.history_len = 0
        self.last_history = 0
        self.call = None    # 对于二人聊天，对房间的称呼应该为对方的名字，而不是self.name

    def set(self, name, id, member, owner, user_id = None):
        self.name = name
        self.id = id
        self.owner = owner
        self.member = {}
        for id in member:
            self.member[int(id)] = member[id]
        # 房间名为朋友的名字
        if self.single is True:
            for i in self.member:
                if user_id != i:
                    self.call = self.member[i]

    def update(self, data):
        if data['type'] == 'roomMessage':
            self.history.append(data['user_name']+": "+data['message'])
            self.history_len += 1
        elif data['type'] == 'remindFile':
            self.history.append('收到了来自%s的文件<%s>,要下载吗'%(data['user_name'], data['file_name']))
            self.history_len += 1

class UI(tk.Frame):
    def __init__(self, sock):
        super(UI, self).__init__()
        self.initLayout()

        self.sock = sock
        self.rooms = {}     # 管理该用户所在的房间
        self.friends = {}
        self.name = None
        self.id = None
        self.curPos = None  #用户所在的位置（某个房间或用户）
        self.showRow = 0 # 左边展示的房间&朋友的
        self.shows = []

    def recv(self):
        print('等候接收了')
        pre_data = self.sock.recv(50)
        pre_data = json.loads(pre_data.decode('utf-8').strip('\00'))
        if pre_data['type'] == 'len':
            data_len = pre_data['len']
            recv_data = self.sock.recv(data_len).decode('utf-8')
            print('数据长度为%d' % data_len, recv_data)
            return json.loads(recv_data)

    def process(self):
        # 与用户界面“并行”的与服务器打交道的线程
        #0.接收服务器发来的配置信息
        recv_data = self.recv()
        if recv_data['type'] == 'initUser':
            self.name = recv_data['name']
            self.id = recv_data['id']
            self.master.title('%s-Mini Chat!'%self.name)

        #1.接收公共房间的信息
        recv_data = self.recv()
        if recv_data['type'] == 'selfEnterRoom':
            room = Room(single=False)
            room.set(recv_data['room_name'], recv_data['room_id'], recv_data['member'], recv_data['owner'])
            self.rooms[room.id] = room
            self.curPos = room
            self.showRoom(room)      # 显示该房间

        while True:
            recv_data = self.recv()
            if recv_data['type'] == 'otherEnterRoom':
                room = self.rooms[recv_data['room_id']]
                room.member[recv_data['user_id']] = [recv_data['user_name']]
            elif recv_data['type'] == 'selfEnterRoom':
                room = Room(single=recv_data['single'])
                room.set(recv_data['room_name'], recv_data['room_id'], recv_data['member'], recv_data['owner'], self.id)
                self.rooms[room.id] = room
                self.showRoom(room)    # 在窗口左侧显示该房间
            elif recv_data['type'] == 'roomMessage' :
                room = self.rooms[recv_data['room_id']]
                room.update(recv_data)
            elif recv_data['type'] == 'remindFile':
                room = self.rooms[recv_data['room_id']]
                room.update(recv_data)
            elif recv_data['type'] == 'fileShare':
                # 用户向服务器请求传输文件后，服务器对用户的响应
                port = recv_data['port']
                t = threading.Thread(target=self.processShareFile, args=(host, port, self.file_name, self.curPos))
                t.start()
            self.updateCurrent()

    def showRoom(self, room):
        # print('showRoom: %s'%room.name)
        name = room.name
        pre_name = '群聊'
        if room.single is True:
            name = room.call
            pre_name = '朋友'

        but = tk.Button(self.frame1, activebackground = '#dddddd', bg = '#cccccc', justify = tk.CENTER,
                        width = 28, height = 2,
                        text = '%s：%s'%(pre_name, name), command=lambda :self.clickLeftBut(room))
        but.grid(row = self.showRow)
        self.showRow += 1
        self.shows.append(but)


    def clickLeftBut(self, room):
        # print('clickLeftBut: %s'%room.name)
        if room == self.curPos:
            return
        self.curPos = room
        if room.single:
            self.name_label['text'] = self.curPos.call
        else:
            self.name_label['text'] = self.curPos.name
        self.hist_box.delete(0.0, tk.END)
        for i in range(room.history_len):
            self.hist_box.insert(tk.END, room.history[i] +'\n')
        room.last_history = room.history_len

    def updateCurrent(self):
        # print('updateCurrent')
        for i in range(self.curPos.last_history, self.curPos.history_len):
            self.hist_box.insert(tk.END, self.curPos.history[i] + '\n')
        self.curPos.last_history = self.curPos.history_len

    def initLayout(self):
        self.grid()
        self.frame0 = tk.Frame(self, width = 200, height = 38, bg = '#cccccc')
        self.frame1 = tk.Frame(self, width = 200, height = 462, bg = '#cccccc')      # 在界面左侧，群聊列表（竖排）
        self.frame2 = tk.Frame(self, width = 600, height = 38, bg = '#eeeeee')       # 在界面右侧顶部，显示当前群聊名称
        dummy1 = tk.Frame(self, width = 600, height = 1, bg = '#999999')
        self.frame3 = tk.Frame(self, width = 600, height = 330, bg = '#eeeeee')      # 在界面右侧中部，历史信息
        dummy2 = tk.Frame(self, width=600, height=1, bg='#999999')
        self.frame4 = tk.Frame(self, width = 600, height = 100, bg = '#eeeeee')       # 在界面右侧下部，为输入信息框
        dummy3 = tk.Frame(self, width=600, height=1, bg='#999999')
        self.frame5 = tk.Frame(self, width = 600, height = 30, bg = '#eeeeee')       # 在界面右侧底部，有发送等按钮

        self.frame0.grid(row=0, column = 0)
        self.frame1.grid(row = 1, column = 0, rowspan = 6)
        self.frame2.grid(row = 0, column = 1)
        dummy1.grid(row = 1, column = 1)
        self.frame3.grid(row = 2, column = 1)
        dummy2.grid(row = 3, column = 1)
        self.frame4.grid(row = 4, column = 1)
        dummy3.grid(row = 5, column = 1)
        self.frame5.grid(row = 6, column = 1)

        self.search_box = tk.Label(self.frame0, text = '             ', bg = '#cccccc',font = font.Font(family='楷体', size = 17))
        self.search_box.grid(row = 0, column = 0)
        self.search_box.columnconfigure(0, weight = 3)
        self.create_btn = tk.Button(self.frame0, text = '╋', width = 2, height = 1,bg = '#cccccc', font = font.Font(family='楷体', size = 17),
                                    command = self.createRoom)
        self.create_btn.grid(row = 0, column = 1)
        self.create_btn.columnconfigure(1, weight = 1)

        self.name_label = tk.Label(self.frame2, text = '公众聊天室', font = font.Font(family='楷体', size = 17))
        self.name_label.grid()

        self.hist_box = tk.Text(self.frame3, bg='#eeeeee', height = 20,font = font.Font(family='新宋', size = 13))
        self.hist_box.grid()

        self.input_box = tk.Text(self.frame4, bg='#eeeeee',height = 6, font = font.Font(family='新宋', size = 13))
        self.input_box.grid()

        self.send_btn = tk.Button(self.frame5, text = '发送', command=lambda :self.clickSendBtn())
        self.send_btn.grid(row = 0, column = 0)
        self.send_btn = tk.Button(self.frame5, text = '文件', command=lambda :self.clickFileBtn())
        self.send_btn.grid(row = 0, column = 1)

        self.frame1.grid_propagate(0)
        self.frame2.grid_propagate(0)
        self.frame3.grid_propagate(0)
        self.frame4.grid_propagate(0)
        self.frame5.grid_propagate(0)
        self.grid_propagate()

    def clickSendBtn(self):
        message = self.input_box.get(0.0, tk.END).strip()
        print('message:', message)
        if len(message) == 0:
            return
        send_data = {}

        send_data['type'] = 'roomMessage'
        send_data['room_id'] = self.curPos.id
        send_data['user_name'] = self.name
        send_data['message'] = message
        self.curPos.update(send_data)
        self.updateCurrent()
        send_data = json.dumps(send_data)
        self.sendInfo(send_data.encode('utf-8'))

    def clickFileBtn(self):
        self.file_name = filedialog.askopenfilename()
        if not self.file_name:
            return
        self.curPos.history.append(self.name+': '+'文件发送中...')
        self.curPos.history_len += 1
        self.updateCurrent()

        send_data = {'type': 'fileShare'}
        send_data['room_id'] = self.curPos.id
        send_data = json.dumps(send_data).encode('utf-8')
        self.sendInfo(send_data)

        # 等待服务器回复
        # 在process函数中等候

    def processShareFile(self, host, port, file_name, curPos):
        # 客户端新开的向服务器传输文件的线程
        try:
            csock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            csock.connect((host, port))
            #提前发送一个包，包含文件名和文件大小。该包有128个字符+一个整数长
            pre_data = struct.pack('128sl', os.path.basename(file_name).encode('utf-8'), os.stat(file_name).st_size)
            csock.send(pre_data)
            f = open(file_name, 'rb')
            while True:
                pData = f.read(1024)
                if not pData:
                    break
                csock.send(pData)
            f.close()

            curPos.history.append(self.name + ': ' + '文件发送成功:)')
        except:
            curPos.history.append(self.name+': '+'文件发送失败:(')
        csock.close()
        self.curPos.history_len += 1
        self.updateCurrent()

        print('分享文件的线程结束了！')

    def sendInfo(self, send_data):
        try:
            pre_data = {'type': 'len'}
            pre_data['len'] = len(send_data)
            pre_data = json.dumps(pre_data).encode('utf-8')
            pre_data = struct.pack('50s', pre_data)
            self.sock.send(pre_data)
            self.sock.sendall(send_data)
            return True
        except:
            return False

    def createRoom(self):
        pass

host = '127.0.0.1'
port = 8000
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.connect((host, port))

app = UI(sock=sock)
app.master.title('Mini Chat!')
t = threading.Thread(target=app.process)
t.start()
app.mainloop()

