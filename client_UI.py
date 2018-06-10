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
        self.another = None    # 对于二人聊天，对房间的称呼应该为对方的名字，而不是self.name

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
                    self.another = (i, self.member[i])

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
        self.curRoom = None  #用户所在的位置（某个房间或用户）
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
            room.member[self.id] = self.name
            self.rooms[room.id] = room
            self.curRoom = room
            self.showRoom(room)      # 显示该房间

        while True:
            recv_data = self.recv()
            if recv_data['type'] == 'otherEnterRoom':
                room = self.rooms[recv_data['room_id']]
                room.member[recv_data['user_id']] = recv_data['user_name']
            elif recv_data['type'] == 'selfEnterRoom':
                room = Room(single=recv_data['single'])
                room.set(recv_data['room_name'], recv_data['room_id'], recv_data['member'], recv_data['owner'], self.id)
                self.rooms[room.id] = room
                self.showRoom(room)    # 在窗口左侧显示该房间
                if room.single is True:
                    # 添加到我的朋友
                    friend_id = room.another[0]
                    friend_name = room.another[1]
                    self.friends[friend_id] = friend_name
            elif recv_data['type'] == 'roomMessage' :
                room = self.rooms[recv_data['room_id']]
                room.update(recv_data)
            elif recv_data['type'] == 'remindFile':
                room = self.rooms[recv_data['room_id']]
                room.update(recv_data)
            elif recv_data['type'] == 'fileShare':
                # 用户向服务器请求传输文件后，服务器对用户的响应
                port = recv_data['port']
                t = threading.Thread(target=self.processShareFile, args=(host, port, self.file_name, self.curRoom))
                t.start()
            self.updateCurrent()

    def showRoom(self, room):
        # print('showRoom: %s'%room.name)
        name = room.name
        pre_name = '群聊'
        if room.single is True:
            name = room.another[1]
            pre_name = '朋友'

        but = tk.Button(self.frame1, activebackground = '#dddddd', bg = '#cccccc', justify = tk.CENTER,
                        width = 28, height = 2,
                        text = '%s：%s'%(pre_name, name), command=lambda :self.clickLeftBut(room))
        but.grid(row = self.showRow)
        self.showRow += 1
        self.shows.append(but)


    def clickLeftBut(self, room):
        # print('clickLeftBut: %s'%room.name)
        if room == self.curRoom:
            return
        self.curRoom = room
        if room.single:
            self.name_label['text'] = self.curRoom.another[1]
        else:
            self.name_label['text'] = self.curRoom.name
        self.hist_box.delete(0.0, tk.END)
        for i in range(room.history_len):
            self.hist_box.insert(tk.END, room.history[i] +'\n')
        room.last_history = room.history_len

    def updateCurrent(self):
        # print('updateCurrent')
        for i in range(self.curRoom.last_history, self.curRoom.history_len):
            self.hist_box.insert(tk.END, self.curRoom.history[i] + '\n')
        self.curRoom.last_history = self.curRoom.history_len

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
        self.name_label.grid(row = 0, column = 0)
        self.room_set = tk.Button(self.frame2, text = '更多', font = font.Font(family='楷体', size = 17),
                                     command = self.clickRoomSet)
        self.room_set.grid(row = 0, column = 1)
        self.room_set.place(x = 520, y = 0)

        self.hist_box = tk.Text(self.frame3, bg='#eeeeee', height = 20,font = font.Font(family='新宋', size = 13))
        self.hist_box.grid()

        self.input_box = tk.Text(self.frame4, bg='#eeeeee',height = 6, font = font.Font(family='新宋', size = 13))
        self.input_box.grid()

        send_btn = tk.Button(self.frame5, text = '发送', command=lambda :self.clickSendBtn(),font = font.Font(family='新宋', size = 13))
        send_btn.grid(row = 0, column = 0)
        send_btn.place(x = 490, y = 0)
        file_btn = tk.Button(self.frame5, text = '文件', command=lambda :self.clickFileBtn(),font = font.Font(family='新宋', size = 13))
        file_btn.grid(row = 0, column = 1)
        file_btn.place(x = 540, y = 0)


        self.frame1.grid_propagate(0)
        self.frame2.grid_propagate(0)
        self.frame3.grid_propagate(0)
        self.frame4.grid_propagate(0)
        self.frame5.grid_propagate(0)
        self.grid_propagate()

    def clickRoomSet(self):
        # 朋友和群显示的不一样
        f = font.Font(family='楷体', size = 17)
        if self.curRoom.single is True:
            width = 200
            height = 150
            c = tk.Toplevel()
            c.title('关于该房间')
            c.minsize(width, height)
            c.maxsize(width, height)
            c.geometry('%dx%d+%d+%d' % (width, height, (c.winfo_screenwidth() - width) / 2, (c.winfo_screenheight() - height) / 2))
            n = tk.Label(c, text='好友：%s'%self.curRoom.another[1], font = f)
            n.grid()
            n.place(x=30, y=50)
        else:
            width = 400
            height = 500
            c = tk.Toplevel()
            c.title('关于该房间')
            c.minsize(width, height)
            c.maxsize(width, height)
            c.geometry('%dx%d+%d+%d' % (width, height, (c.winfo_screenwidth() - width) / 2, (c.winfo_screenheight() - height) / 2))

            def seeMember(room):
                print(room.member)
                all_member = tk.Text(c, font=f, bg='#fefeee')
                for id in room.member:
                    all_member.insert(tk.END, room.member[id] + '\n')
                all_member.place(x=0, y=90)

            def quitRoom(room):
                # 群员退出群
                pass

            def dissoRoom(room):
                # 群主解散群
                pass

            info = tk.Label(c, text = '群聊：%s'%(self.curRoom.name), font = f)
            info.place(x = 100, y = 0)
            see = tk.Button(c, text = '查看群成员', font = f, command = lambda :seeMember(self.curRoom))

            see.place(x = 50, y = 50)
            if self.id == self.curRoom.owner:
                disso = tk.Button(c, text = '解散该群', font = f, command = lambda :dissoRoom(self.curRoom))
                disso.place(x = 230, y = 50)
            else:
                quit = tk.Button(c, text = '退出该群', font = f, command = lambda :quitRoom(self.curRoom))
                quit.place(x = 230, y = 50)

    def clickSendBtn(self):
        message = self.input_box.get(0.0, tk.END).strip()
        print('message:', message)
        if len(message) == 0:
            return
        send_data = {}

        send_data['type'] = 'roomMessage'
        send_data['room_id'] = self.curRoom.id
        send_data['user_name'] = self.name
        send_data['message'] = message
        self.curRoom.update(send_data)
        self.updateCurrent()
        send_data = json.dumps(send_data)
        self.sendInfo(send_data.encode('utf-8'))

    def clickFileBtn(self):
        self.file_name = filedialog.askopenfilename()
        if not self.file_name:
            return
        self.curRoom.history.append(self.name+': '+'文件发送中...')
        self.curRoom.history_len += 1
        self.updateCurrent()

        send_data = {'type': 'fileShare'}
        send_data['room_id'] = self.curRoom.id
        send_data = json.dumps(send_data).encode('utf-8')
        self.sendInfo(send_data)

        # 等待服务器回复
        # 在process函数中等候

    def processShareFile(self, host, port, file_name, curRoom):
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

            curRoom.history.append(self.name + ': ' + '文件发送成功:)')
        except:
            curRoom.history.append(self.name+': '+'文件发送失败:(')
        csock.close()
        self.curRoom.history_len += 1
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
        width = 400
        height = 500
        c = tk.Toplevel()
        c.title('选择群成员')
        c.minsize(width, height)
        c.maxsize(width, height)
        c.geometry('%dx%d+%d+%d' % (width, height, (c.winfo_screenwidth() - width) / 2, (c.winfo_screenheight() - height) / 2))

        def clickSure():
            choices = []
            for id in all_r:
                if all_r[id].get() == 1:
                    choices.append(id)
            if len(choices) != 0:
                choices.append(self.id)
                send_data = {'type': 'createRoom'}
                send_data['member'] = choices
                send_data = json.dumps(send_data).encode('utf-8')
                self.sendInfo(send_data)
            c.destroy()

        cur_row = 0
        all_r = {}
        if len(self.friends) != 0:
            for id in self.friends:
                v = tk.IntVar()     #判断该朋友是否被选中
                r = tk.Checkbutton(c, text = self.friends[id], width = 9, font = font.Font(family='楷体', size = 17),
                                   variable = v, bg = '#eeeeee')
                r.grid(row = cur_row, column = 0)
                all_r[id] = v
                cur_row += 1

        else:
            note = tk.Label(c, text = '当前无好友', font = font.Font(family='楷体', size = 17))
            note.grid()
            note.place(x = 150, y = 280)

        sure = tk.Button(c, text = '确定', font = font.Font(family='楷体', size = 17), bg = '#eeeeee',
                         command = lambda: clickSure())
        sure.grid(row = cur_row, column = 0)
        sure.place(x = 330, y = 450)



host = '127.0.0.1'
port = 8000
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.connect((host, port))

app = UI(sock=sock)
app.master.title('Mini Chat!')
t = threading.Thread(target=app.process)
t.start()
app.mainloop()

