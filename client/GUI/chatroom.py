from tkinter import *
from tkinter import filedialog
import sys
import os
sys.path.append('..')
from client_session import *
import datetime
import socket
import struct
import threading

class ChatroomUI:
    def __init__(self, session, usr_name, **args):
        self.session = session
        #self.session.msg_func = self.msg_func
        self.usr_name = usr_name
        self.rooms = {}
        tk = Tk()
        self.tk = tk
        # 默认字体
        ft = font.Font(family='Times New Roman', size=15)
        self.ft = ft

        # 主界面
        tk.title('Main')
        self.main_part = Room(self)
        '''
        width, height = 500, 400
        tk.minsize(width, height)
        tk.maxsize(width, height)
        tk.geometry('%dx%d+%d+%d' % (width,height,(tk.winfo_screenwidth() - width ) / 2, (tk.winfo_screenheight() - height) / 2))
        Label(tk, text=usr_name, font=ft).place(x=70, y=60)

        but_m = Button(tk, text='Messages', font=ft, command=lambda:self.ShowMessages())
        but_m.place(x=250, y=60)

        but_s = Button(tk, text='Setting', font=ft, command=lambda:self.ShowSetting())
        but_s.place(x=70, y=150)

        but_af = Button(tk, text='Add friend', font=ft, command=lambda:self.AddFriend())
        but_af.place(x=250, y=150)        


        but_f = Button(tk, text='My friends', font=ft, command=lambda:self.ShowFriends())
        but_f.place(x=70, y=240)

        but_mcr = Button(tk, text='My chat rooms', font=ft, command=lambda:self.ShowChatRooms())
        but_mcr.place(x=250, y=240)        

        but_ecr = Button(tk, text='Enter chat room', font=ft, command=lambda:self.EnterChatRoom())
        but_ecr.place(x=70, y=330)


        but_ccr = Button(tk, text='Create chat room', font=ft, command=lambda:self.CreateChatRoom())
        but_ccr.place(x=250, y=330)
        '''
        tk.protocol('WM_DELETE_WINDOW', lambda:self.logout())
        self.friendlist = None
        self.chatrooms = None
        self.tk.after(0, self.loop)

    def loop(self):
        js = None
        try:
            js = self.session.queue.get_nowait()
        except:
            js = None
        if js is not None:
            self.msg_func(js)
        self.tk.after(500, self.loop)

    def msg_func(self, js):
        print('&')
        if js['type'] == 'person_speak':
            room_name = js['group_name']
            self.main_part.recv_msg(room_name, js['date_time'] + '\n' + js['usr_name']+': '+js['message'])
        elif js['type'] == 'person_in':
            room_name = js['group_name']
            self.main_part.person_in(room_name, js['usr_name'])
        elif js['type'] == 'person_out':
            room_name = js['group_name']
            self.main_part.person_out(room_name, js['usr_name'])
        elif js['type'] == 'person_share_file':
            room_name = js['group_name']
            self.main_part.get_file(room_name, js)
        elif js['type'] == 'usr_removed':
            room_name = js['group_name']
            self.main_part.usr_removed(room_name)
        elif js['type'] == 'usr_invited':
            room_name = js['group_name']
            self.main_part.newroom(room_name)

    def logout(self):
        self.tk.destroy()
        self.session.logout(self.usr_name)

    def ShowFriends(self):
        try:
            assert self.friendlist.winfo_exists()==1
        except:
            fl = Toplevel(self.tk)
            self.friendlist = fl
            fl.title('Friend list')
            t = Text(fl, borderwidth=0, font=font.Font(family='Times New Roman', size=18))
            bar = Scrollbar(fl)
            bar.config(command=t.yview)
            t.config(yscrollcommand=bar.set,width=20,height=20,background='#ffffff')
            bar.pack(side=RIGHT,fill=Y)
            t.pack(side=LEFT,fill=BOTH)
            lst = self.session.get_friend_list(self.usr_name)
            self.t=t
            t.insert(END, '\n'.join(lst))
            t['state']='disabled'

    def AddFriend(self):
        tl = Toplevel(self.tk)
        tl.title('Add friend')
        width, height = 500, 400
        tl.minsize(width, height)
        tl.maxsize(width, height)
        Label(tl, text='User name: ', font=self.ft).place(x=50, y=150)
        Label(tl, text='Verification: ', font=self.ft).place(x=50, y=190)
        
        var_usr_name = StringVar()
        entry_usr_name = Entry(tl, textvariable=var_usr_name, font=self.ft)
        entry_usr_name.place(x=200, y=150)
        self.entry_usr_name = entry_usr_name
        var_vm = StringVar()
        entry_vm = Entry(tl, textvariable=var_vm, font=self.ft)
        entry_vm.place(x=200, y=190)
        self.entry_vm = entry_vm

        but_sd = Button(tl, text='send', font=self.ft, command=lambda:self.send_friend_request(tl))
        but_sd.place(x=170, y=240)
    def send_friend_request(self, tl):
        friend_name = self.entry_usr_name.get()
        vm = self.entry_vm.get()
        status, msg = self.session.send_friend_request(self.usr_name, friend_name, vm)
        if status:
            messagebox.showinfo('Succeed', msg)
            tl.destroy()
        else:
            messagebox.showerror('Fail', msg)

    def ShowChatRooms(self):
        try:
            assert self.chatrooms.winfo_exists()==1
        except:
            status, msg = self.session.get_chat_rooms(self.usr_name)
            if not status:
                messagebox.showerror('Fail', msg)
            else:
                lst = msg
            cr = Toplevel(self.tk)
            self.chatrooms = cr
            cr.title('Chat room list')
            t = Canvas(cr)
            bar = Scrollbar(cr)
            bar.config(command=t.yview)
            t.config(yscrollcommand=bar.set,height=20+60*len(lst),width=200)
            for i, cid in enumerate(lst):
                Button(t, text=str(cid), font=self.ft, command=lambda:self.OpenChatRoom(cid)).place(y=20+i*60,x=20)
            bar.pack(side=RIGHT,fill=Y)
            t.pack(side=LEFT,fill=BOTH)

    def EnterChatRoom(self):
        tl = Toplevel(self.tk)
        tl.title('Enter chat room')
        width, height = 500, 400
        tl.minsize(width, height)
        tl.maxsize(width, height)
        Label(tl, text='Room name: ', font=self.ft).place(x=50, y=150)
        Label(tl, text='Password: ', font=self.ft).place(x=50, y=190)
        
        RN = Entry(tl, font=self.ft)
        RN.place(x=200, y=150)
        PW = Entry(tl, font=self.ft)
        PW.place(x=200, y=190)

        but_sd = Button(tl, text='send', font=self.ft, command=lambda:self.enter_chat_room_request(RN, PW, tl))
        but_sd.place(x=170, y=240)
    def enter_chat_room_request(self, RN, PW, tl):
        room_name , password = RN.get(), PW.get()
        status, msg = self.session.enter_chat_room_request(self.usr_name, room_name, password)
        if status:
            messagebox.showinfo('Succeed', msg)
            tl.destroy()
            self.OpenChatRoom(room_name)
        else:
            messagebox.showerror('Fail', msg)

    def CreateChatRoom(self):
        tl = Toplevel(self.tk)
        tl.title('Create chat room')
        width, height = 500, 400
        tl.minsize(width, height)
        tl.maxsize(width, height)
        Label(tl, text='Room name: ', font=self.ft).place(x=50, y=150)
        Label(tl, text='Password: ', font=self.ft).place(x=50, y=190)
        
        RN = Entry(tl, font=self.ft)
        RN.place(x=200, y=150)
        PW = Entry(tl, font=self.ft)
        PW.place(x=200, y=190)

        but_sd = Button(tl, text='send', font=self.ft, command=lambda:self.create_chat_room_request(RN, PW, tl))
        but_sd.place(x=170, y=240)
        '''
    def create_chat_room_request(self, RN, PW, tl):
        room_name , password = RN.get(), PW.get()
        status, msg = self.session.create_chat_room_request(self.usr_name, room_name, password)
        if status:
            messagebox.showinfo('Succeed', msg)
            tl.destroy()
            self.OpenChatRoom(room_name)
        else:
            messagebox.showerror('Fail', msg)
            
    def ShowMessages(self):
        pass

    def ShowSetting(self):
        pass
    
    def OpenChatRoom(self, room_name):
        status, info = self.session.get_room_info(self.usr_name, room_name)
        if not status:
            messagebox.showerror('Fail', info)
            return
        self.rooms[room_name] = Room(self, info)'''

class Room:
    def __init__(self, UI):
        self.UI = UI
        self.tk = UI.tk
        self.usr_name = UI.usr_name
        self.ft = UI.ft
        room_name = 'Hall' #info['group_name']
        self.room_name = room_name
        self.all_rooms = {}
        tl = self.tk #Toplevel(self.tk)
        #tl.title('Chat room %s'%room_name)
        self.store_dir = os.getcwd()        #下载的文件的安放路径
        width, height = 500, 400
        tl.minsize(width, height)
        self.tl = tl
        # 房间信息、房主设置
        row = Frame(tl)
        Label(row, text='用户名: '+self.usr_name, font=self.ft).place(relx=0.01, rely=0., relwidth=0.13, relheight=1.)
        self.RN = Label(row, text='房间名: '+room_name, font=self.ft)
        self.RN.place(relx=0.15, rely=0., relwidth=0.13, relheight=1.)
        setting_act = lambda:self.chat_room_setting()
        Button(row, text='房间设置', font=self.ft, command=setting_act).place(relx=0.29, rely=0., relwidth=0.13, relheight=1.)
        setting_act = lambda:self.personal_setting()
        Button(row, text='个人设置', font=self.ft, command=setting_act).place(relx=0.43, rely=0., relwidth=0.13, relheight=1.)
        setting_act = lambda:self.add_friend()
        Button(row, text='好友添加', font=self.ft, command=setting_act).place(relx=0.57, rely=0., relwidth=0.13, relheight=1.)
        setting_act = lambda:self.create_chat_room()
        Button(row, text='创建房间', font=self.ft, command=setting_act).place(relx=0.71, rely=0., relwidth=0.13, relheight=1.)
        setting_act = lambda:self.verification_message()
        Button(row, text='验证消息', font=self.ft, command=setting_act).place(relx=0.85, rely=0., relwidth=0.13, relheight=1.)
        row.place(relx=0., rely=0., relwidth=1., relheight=0.1)
        

        # 输入框
        row = Frame(tl)
        input_box = Text(row, font=self.ft)
        input_box.place(relx=0., rely=0., relwidth=0.62, relheight=0.95)
        self.input_box = input_box

        but_sd = Button(row, text='发送', font=self.ft, command=lambda:self.send_msg())
        but_sd.place(relx=0.64, rely=0.3, relwidth=0.1, relheight=0.6)

        but_cl = Button(row, text='清空历史', font=self.ft, command=lambda:self.clear_msg())
        but_cl.place(relx=0.76, rely=0.3, relwidth=0.1, relheight=0.6)

        but_sf = Button(row, text = '文件', font = self.ft, command=lambda:self.share_file(self.room_name))
        but_sf.place(relx=0.88, rely=0.3, relwidth=0.1, relheight=0.6)
        row.place(relx=0.3, rely=0.8, relwidth=0.7, relheight=0.2)

        # 群列表
        f = Frame(tl)
        room_list = Listbox(f, font=self.ft)
        self.room_list = room_list
        bar = Scrollbar(f)
        bar.config(command=room_list.yview)
        room_list.config(yscrollcommand=bar.set)
        bar.place(relx=0.9, rely=0.01, width=20, relheight=.98)
        room_list.place(relx=0.0, rely=0.01, relwidth=0.9, relheight=.98)
        room_list.bind('<Double-Button-1>', lambda event:self.click_room())
        f.place(relx = 0.03, rely= 0.1, relwidth=0.27, relheight=0.45)
        
        

        # 好友列表
        f = Frame(tl)
        friend_list = Listbox(f, font=self.ft)
        self.friend_list = friend_list
        bar = Scrollbar(f)
        bar.config(command=friend_list.yview)
        friend_list.config(yscrollcommand=bar.set)
        bar.place(relx=0.9, rely=0.01, width=20, relheight=.98)
        friend_list.place(relx=0.0, rely=0.01, relwidth=0.9, relheight=.98)
        friend_list.bind('<Double-Button-1>', lambda event:self.click_friend())
        f.place(relx = 0.03, rely= 0.55, relwidth=0.27, relheight=0.45)

        # 刷新群列表和好友列表
        self.flush_list()

        # 文件列表
        f = Frame(tl)
        t = Listbox(f, font=self.ft)
        bar = Scrollbar(f)
        bar.config(command=t.yview)
        t.config(yscrollcommand=bar.set)
        bar.place(relx=0.9, rely=0.01, width=20, relheight=.98)
        t.place(relx=0.0, rely=0.01, relwidth=0.9, relheight=.98)
        t.bind('<Double-Button-1>', lambda event:self.download_file())
        self.file_listbox = t
        f.place(relx=0.8, rely=0.1, relwidth=0.2, relheight=0.3)
        
        # 成员
        f0 = Frame(tl)
        t = Text(f0, font=self.ft)
        bar = Scrollbar(f0)
        bar.config(command=t.yview)
        t.config(yscrollcommand=bar.set)
        bar.place(relx=0.9, rely=0.01, width=20, relheight=.98)
        t.place(relx=0.0, rely=0.01, relwidth=0.9, relheight=.98)
        t['state']='disabled'
        self.usr_box = t
        f0.place(relx=0.8, rely=0.4, relwidth=0.2, relheight=0.4)

        # 历史消息
        
        row = Frame(tl)
        t = Text(row, font=self.ft)
        bar = Scrollbar(row)
        bar.config(command=t.yview)
        t.config(yscrollcommand=bar.set)
        bar.place(relx=0.97, rely=0.01, width=20, relheight=.98)
        t.place(relx=0.01, rely=0.01, relwidth=0.96, relheight=.98)
        row.place(relx=0.3, rely=0.1, relwidth=0.5, relheight=0.7)
        t['state']='disabled'
        hist_box = t
        self.hist_box = hist_box

        #tl.protocol('WM_DELETE_WINDOW', lambda:self.leave(room_name))

    def click_room(self):
        lb = self.room_list
        try:
            rn = lb.get(lb.curselection())
        except:
            return
        #self.UI.session.enter_chat_room_request(self.usr_name, rn, '')
        self.flush_room(rn)

    def click_friend(self):
        lb = self.friend_list
        try:
            fn = lb.get(lb.curselection())
        except:
            return
        self.flush_room(fn, isfriend=True)

    def personal_setting(self):
        tl = Toplevel(self.tk)
        tl.title('setting')
        width, height = 500, 300
        tl.minsize(width, height)
        tl.maxsize(width, height)
        tl.geometry('%dx%d+%d+%d' % (width,height,(tl.winfo_screenwidth() - width ) / 2, (tl.winfo_screenheight() - height) / 2))
        Label(tl, text='old password: ', font=self.ft).place(x=40, y=50)
        Label(tl, text='new password: ', font=self.ft).place(x=40, y=100)
        Label(tl, text='confirm password: ', font=self.ft).place(x=40, y=150)
        o = Entry(tl, show='*', font=self.ft)
        o.place(x=220, y=50)
        n = Entry(tl, show='*', font=self.ft)
        n.place(x=220, y=100)
        c = Entry(tl, show='*', font=self.ft)
        c.place(x=220, y=150)
        Button(tl, text='change password', font=self.ft, command=lambda:self.change_password(o, n, c, tl)).place(x=150, y=200)
    def change_password(self, o, n, c, tl):
        op = o.get()
        np = n.get()
        cp = c.get()
        if np!=cp:
            messagebox.showerror('Fail', 'New password does not match.')
            return
        status, msg = self.UI.session.change_password_request(self.usr_name, op, np)
        if status:
            messagebox.showinfo('Succeed', msg)
            tl.destroy()
        else:
            messagebox.showerror('Fail', msg)

    def add_friend(self):
        tl = Toplevel(self.tk)
        tl.title('add friend')
        width, height = 500, 200
        tl.minsize(width, height)
        tl.maxsize(width, height)
        tl.geometry('%dx%d+%d+%d' % (width,height,(tl.winfo_screenwidth() - width ) / 2, (tl.winfo_screenheight() - height) / 2))
        Label(tl, text='friend name: ', font=self.ft).place(x=40, y=50)
        Label(tl, text='verification: ', font=self.ft).place(x=40, y=100)
        fn = Entry(tl, font=self.ft)
        fn.place(x=220, y=50)
        ver = Entry(tl, font=self.ft)
        ver.place(x=220, y=100)
        Button(tl, text='send', font=self.ft, command=lambda:self.add_friend_request(fn, ver, tl)).place(x=150, y=150)
    def add_friend_request(self, fn, ver, tl):
        friend_name = fn.get()
        verification = ver.get()
        status, msg = self.UI.session.add_friend_request(self.usr_name, friend_name, verification)
        if status:
            messagebox.showinfo('Succeed', msg)
            tl.destroy()
        else:
            messagebox.showerror('Fail', msg)
        
    def create_chat_room(self):
        tl = Toplevel(self.tk)
        tl.title('Create chat room')
        width, height = 500, 200
        tl.minsize(width, height)
        tl.maxsize(width, height)
        tl.geometry('%dx%d+%d+%d' % (width,height,(tl.winfo_screenwidth() - width ) / 2, (tl.winfo_screenheight() - height) / 2))
        Label(tl, text='room name: ', font=self.ft).place(x=50, y=50)
        #Label(tl, text='Password: ', font=self.ft).place(x=50, y=190)
        RN = Entry(tl, font=self.ft)
        RN.place(x=200, y=50)
        #PW = Entry(tl, font=self.ft)
        #PW.place(x=200, y=190)
        but_sd = Button(tl, text='create', font=self.ft, command=lambda:self.create_chat_room_request(RN, tl))
        but_sd.place(x=170, y=130)
    def create_chat_room_request(self, RN, tl):
        room_name = RN.get()
        status, msg = self.UI.session.create_chat_room_request(self.usr_name, room_name, password='')
        if status:
            messagebox.showinfo('Succeed', msg)
            #self.flush_list()
            self.room_list.insert(END, room_name)
            self.get_room_info(room_name)
            tl.destroy()
        else:
            messagebox.showerror('Fail', msg)
        
    def verification_message(self):
        f = Toplevel(self.tk)
        f.title('verification')
        width, height = 500, 400
        f.minsize(width, height)
        f.maxsize(width, height)
        f.geometry('%dx%d+%d+%d' % (width,height,(f.winfo_screenwidth() - width ) / 2, (f.winfo_screenheight() - height) / 2))
        lb = Listbox(f, font=self.ft)
        status, msg = self.UI.session.get_verification_message(self.usr_name)
        if not status:
            messagebox.showerror('Fail', msg)
            f.destroy()
            return
        lst = []
        for i in msg:
            lst.append(i+': '+msg[i])
        #lst = ['a: 123', 'b: 456']
        for n in lst:
            lb.insert(END, n)
        bar = Scrollbar(f)
        bar.config(command=lb.yview)
        lb.config(yscrollcommand=bar.set)
        bar.place(relx=0.95, rely=0.01, width=20, relheight=.98)
        lb.place(relx=0.0, rely=0.01, relwidth=0.95, relheight=.98)
        lb.bind('<Double-Button-1>', lambda event:self.click_ver(lb, f))
        
    def click_ver(self, lb, tl):
        try:
            pl = lb.curselection()
            s = lb.get(pl)
        except:
            return
        friend_name = s.split(': ')[0]
        t0 = tl
        tl = Toplevel(t0)
        tl.title('verification')
        width, height = 300, 230
        tl.minsize(width, height)
        tl.maxsize(width, height)
        tl.geometry('%dx%d+%d+%d' % (width,height,(tl.winfo_screenwidth() - width ) / 2, (tl.winfo_screenheight() - height) / 2))
        Label(tl, text=s, font=self.ft).place(x=50, y=50, width=200, height=80)
        Button(tl, text='accept', font=self.ft, command=lambda:self.acc_friend(friend_name, lb, pl, tl)).place(x=60, y=150)
        Button(tl, text='reject', font=self.ft, command=lambda:self.reject_friend(friend_name, lb, pl, tl)).place(x=200, y=150)

    def acc_friend(self, name, lb, pl, tl):
        status, msg = self.UI.session.add_friend_response(self.usr_name, name, True)
        if not status:
            messagebox.showerror('Fail', msg)
            return
        # print('Accpet: '+name)
        tl.destroy()
        lb.delete(pl, pl)
        # self.friend_list.insert(END, name)
    def reject_friend(self, name, lb, pl, tl):
        status, msg = self.UI.session.add_friend_response(self.usr_name, name, False)
        if not status:
            messagebox.showerror('Fail', msg)
            return
        #print('Reject: '+name)
        tl.destroy()
        lb.delete(pl, pl)
        

    def chat_room_setting(self):
        if self.room_name == 'Hall' or self.room_name.startswith('&'):
            messagebox.showerror('Fail', 'Please enter a room first.')
            return
        info = self.all_rooms[self.room_name]
        tl = Toplevel(self.tk)
        tl.title('setting')
        width, height = 500, 400
        tl.minsize(width, height)
        tl.maxsize(width, height)
        tl.geometry('%dx%d+%d+%d' % (width,height,(tl.winfo_screenwidth() - width ) / 2, (tl.winfo_screenheight() - height) / 2))
        # 加人
        f = Frame(tl)
        f.place(relx = 0., rely=0., relwidth=0.5, relheight=1.)
        Label(f, text='invite', font=self.ft).place(relx=0.01, rely=0.01, relwidth=0.99, relheight=0.19)
        lb = Listbox(f, font=self.ft)
        info = self.all_rooms[self.room_name]
        room_member = info['members']
        lst = []
        i = 0
        while True:
            fn = self.friend_list.get(i)
            if fn == '':
                break
            if not fn in room_member:
                lst.append(fn)
            i+=1
        for n in lst:
            #if n == self.usr_name:
            #    continue
            lb.insert(END, n)
        bar = Scrollbar(f)
        bar.config(command=lb.yview)
        lb.config(yscrollcommand=bar.set)
        bar.place(relx=0.90, rely=0.21, width=20, relheight=.78)
        lb.place(relx=0.0, rely=0.21, relwidth=0.9, relheight=.78)
        lb0 = lb
        lb.bind('<Double-Button-1>', lambda event:self.invite_friend(lb0, tl))
        # 踢人
        f = Frame(tl)
        f.place(relx = 0.5, rely=0., relwidth=0.5, relheight=1.)
        Label(f, text='remove', font=self.ft).place(relx=0.01, rely=0.01, relwidth=0.99, relheight=0.19)
        lb = Listbox(f, font=self.ft)
        for n in room_member:
            lb.insert(END, n)
        bar = Scrollbar(f)
        bar.config(command=lb.yview)
        lb.config(yscrollcommand=bar.set)
        bar.place(relx=0.90, rely=0.21, width=20, relheight=.78)
        lb.place(relx=0.0, rely=0.21, relwidth=0.9, relheight=.78)
        lb.bind('<Double-Button-1>', lambda event:self.kick_person(lb, tl, info['creator']))
    def invite_friend(self, lb, tl):
        if self.room_name.startswith('&') or self.room_name == 'Hall':
            messagebox.showerror('Fail', 'Please enter a room first.')
            return
        try:
            pl = lb.curselection()
            s = lb.get(pl)
        except:
            return
        status, msg = self.UI.session.invite_friend(self.usr_name, s, self.room_name)
        if not status:
            messagebox.showerror('Fail', msg)
            return
        #print('invite: '+s)
    def kick_person(self, lb, tl, creator):
        if self.room_name.startswith('&') or self.room_name == 'Hall':
            messagebox.showerror('Fail', 'Please enter a room first.')
            return
        try:
            pl = lb.curselection()
            s = lb.get(pl)
        except:
            return
        if self.usr_name != creator and self.usr_name != s:
            messagebox.showerror('Fail', 'You are not the creator of the room.')
            return
        status, msg = self.UI.session.remove_person(self.usr_name, s, self.room_name)
        if not status:
            messagebox.showerror('Fail', msg)
            return
        if self.usr_name == s:
            self.room_name = 'Hall'
            self.RN.configure(text='房间名: Hall')
            self.clear_msg()
        #print('kick: '+s)

    def clear_input_box(self):
        self.input_box.delete(0.0,END)

    def get_room_info(self, room_name):
        if not room_name in self.all_rooms:
            status, info = self.UI.session.get_room_info(self.usr_name, room_name)
            if not status:
                messagebox.showerror('Fail', info)
                return
            self.all_rooms[room_name] = info
            tmp = ''
            for msg in info['history']:
                tmp = '%s%s\n%s: %s\n' % (tmp, msg['date_time'], msg['usr_name'], msg['message'])
            info['history'] = tmp

    def flush_list(self):
        status, msg = self.UI.session.get_group_list(self.usr_name)
        if not status:
            messagebox.showerror('Fail', msg)
            return
        lst = msg
        # 为所有房间获取信息，提前缓存防止收到消息时出错
        for room_name in lst:
            self.get_room_info(room_name)
            
        #lst = ['1', '2', '3', '4']
        for n in lst:
            # self.room_list.insert(END, n)
            if not n.startswith('&'):
                self.room_list.insert(END, n)

        status, msg = self.UI.session.get_friend_list(self.usr_name)
        if not status:
            messagebox.showerror('Fail', msg)
            return
        lst = msg
        #lst = ['lrx', 'wy', 'ly', 'qwt']
        for n in lst:
            self.friend_list.insert(END, n)

    # 进入房间时初始化
    def flush_room(self, room_name, isfriend=False):
        prefix = '好友名: ' if isfriend else '房间名: '
        txt = prefix+room_name
        if isfriend:
            friend_name = room_name
            u, v = self.usr_name, friend_name
            if u>v:
                u,v = v,u
            room_name = '&%s&%s'%(u,v)
        self.get_room_info(room_name)
        self.room_name = room_name
        self.RN.configure(text=txt)
        info = self.all_rooms[room_name]
        self.flush_file(info)
        self.flush_member(info)
        self.flush_hist(info)
        self.clear_input_box()

    # 刷新文件列表
    def flush_file(self, info):
        t = self.file_listbox
        t.delete(0, END)
        lst = info['files']
        for i, fn in enumerate(lst):
            t.insert(END, fn)

    # 刷新成员列表
    def flush_member(self, info):
        self.usr_box['state']='normal'
        self.usr_box.delete(0.0, END)
        for m in info['members']:
            self.usr_box.insert(END, m+'\n')
        self.usr_box['state']='disabled'

    # 刷新历史消息
    def flush_hist(self, info):
        self.clear_msg()
        s = info['history'][:-1]
        info['history']=''
        self.recv_msg(self.room_name, s)

    def share_file(self, room_name):
        if room_name == 'Hall':
            messagebox.showerror('提醒', '大厅内不能发送文件')
            return
        file_path = filedialog.askopenfilename()
        if not file_path:
            return
        self.recv_msg(room_name, '文件发送中...')
        file_name = os.path.basename(file_path)
        # status, msg = self.UI.session.share_file(room_name, file_name)
        host, port = self.UI.session.share_file(room_name, file_name)
        if host == '0.0.0.0':
            host = '127.0.0.1'
        print('host:', host, 'port:', port)

        t = threading.Thread(target=self.process_send_file, args=(host, port, room_name, file_path))
        t.start()

    def process_send_file(self, host, port, room_name, file_path):
        # 发送文件的线程
        print('进入线程分享文件了')
        csock = None
        csock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        print('port:', port, type(port), host, type(host))
        csock.connect((host, port))
        print('连接(%s, %d)成功'%(host, port))
        file_name = os.path.basename(file_path)
        file_len = os.stat(file_path).st_size
        pre_data = struct.pack('128sl', file_name.encode('utf-8'), file_len)
        csock.sendall(pre_data)
        print('将发送长为%d的文件%s' % (file_len, file_name))

        f = open(file_path, 'rb')
        buf_len = int(file_len/100)
        buf_len = min(1024, buf_len)
        buf_len = max(300000, buf_len)
        while True:
            buf = f.read(buf_len)
            if not buf:
                break
            csock.sendall(buf)
        f.close()
        print('发送完毕')
        if csock is not None:
            csock.close()


    def get_file(self, room_name, js):
        print('收到文件提醒了')
        user_name = js['usr_name']
        file_name = js['file_name']
        data_time = js['data_time']
        room = self.all_rooms[room_name]
        room['files'].append(file_name)
        if room_name == self.room_name:
            self.file_listbox.insert(END, file_name+'\n')

    def download_file(self):
        if self.room_name == 'Hall':
            messagebox.showerror('提醒', '大厅内不能发送文件')
            return
        try:
            fn = self.file_listbox.get(self.file_listbox.curselection())
            fn = fn.strip()
        except:
            return
        room_name = self.room_name

        print('room_name: %s, Downloading %s:' % (room_name, fn))

        c = Toplevel()
        c.title('下载文件')
        width, height = 300, 200
        c.minsize(width=width, height=height)
        c.maxsize(width=width, height=height)
        c.geometry('%dx%d+%d+%d' % (width, height, (c.winfo_screenwidth() - width) / 2, (c.winfo_screenheight() - height) / 2))
        note = Text(c, width = 30, height = 4,bg = '#efefff', font = font.Font(family='楷体', size = 15))
        note.insert(END, '确定要下载该文件吗?\n文件存放目录为%s'%self.store_dir)
        yes = Button(c, text = '确定', command = lambda :sure())
        no = Button(c, text = '取消', command = lambda :cancle())
        note.place(x = 2, y = 2)
        yes.place(x = 140, y = 150)
        no.place(x = 70, y = 150)

        def cancle():
            c.destroy()

        self = self
        def sure():
            self.true_download_file(room_name, fn)
            c.destroy()

    def true_download_file(self, room_name, file_name):
        # 先向服务器发送请求，说自己要下载文件
        # 与share_file的内容何其类似
        self.recv_msg(room_name, '文件接收中...')
        host, port = self.UI.session.download_file(room_name, file_name)
        if host == '0.0.0.0':
            host = '127.0.0.1'
        print('host:', host, 'port:', port)

        t = threading.Thread(target=self.process_recv_file, args=(host, port, room_name))
        t.start()

    def process_recv_file(self, host, port, room_name):
        # 下载文件的线程
        # 发送文件的线程
        print('进入线程下载文件了')
        csock = None
        file_name = ''
        try:
            csock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            print('port:', port, type(port), host, type(host))
            csock.connect((host, port))
            print('连接(%s, %d)成功'%(host, port))

            pre_data_len = struct.calcsize('128sl')
            pre_data = csock.recv(pre_data_len)
            file_name, file_len = struct.unpack('128sl', pre_data)
            file_name = file_name.decode('utf-8').strip('\00')

            buf_len = int(file_len/100)
            buf_len = min(1024, buf_len)
            buf_len = max(300000, buf_len)
            recv_data = b''
            recv_len = 0
            while recv_len != file_len:
                if recv_len + buf_len < file_len:
                    recv_data += csock.recv(buf_len)
                    recv_len = len(recv_data)   #不能写为recv_len += buf_len
                else:
                    recv_data += csock.recv(file_len-recv_len)
                    recv_len = len(recv_data)
                print('用户接受到的数据长度：', recv_len)
            f = open(os.path.join(os.getcwd(), file_name), 'wb')
            f.write(recv_data)
            f.close()
            print('接收完毕')
            # messagebox.showinfo('文件', '房间%s内的文件%s接收成功'%(room_name, file_name))
        except:
            # messagebox.showinfo('文件', '房间%s内的文件%s接收失败' % (room_name, file_name))
            pass
        if csock is not None:
            csock.close()


    def send_msg(self):
        room_name = self.room_name
        box = self.input_box
        if room_name == 'Hall':
            messagebox.showerror('Fail', 'Please enter a room first.')
            return
        msg = box.get(0.0, END)[:-1]
        self.recv_msg(room_name, datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')+'\n'+self.usr_name+': '+msg)
        status, msg = self.UI.session.send_msg(room_name, msg)
        if not status:
            messagebox.showerror('Fail', msg)
            return
        box.delete(0.0, END)
    def clear_msg(self):
        self.hist_box['state']='normal'
        self.hist_box.delete(0.0, END)
        self.hist_box['state']='disabled'

    def recv_msg(self, room_name, msg):
        info = self.all_rooms[room_name]
        info['history'] = info['history']+str(msg)+'\n'
        if room_name == self.room_name:
            self.hist_box['state']='normal'
            self.hist_box.insert(END, str(msg)+'\n')
            self.hist_box['state']='disabled'

    def person_in(self, room_name, name):
        info = self.all_rooms[room_name]
        info['members'].append(name)
        if room_name == self.room_name:
            self.usr_box['state']='normal'
            self.usr_box.insert(END, name+'\n')
            self.usr_box['state']='disabled'
    def person_out(self, room_name, name):
        info = self.all_rooms[room_name]
        for i, n in enumerate(info['members']):
            if n == name:
                break
        if i < len(info['members']):
            info['members'].pop(i)
        else:
            print('No name %s!\n'%name)
        if room_name == self.room_name:
            self.flush_member(info)
    # 用户被移出群
    def usr_removed(self, room_name):
        self.all_rooms.pop(room_name)
        i = 0
        while True:
            s = self.room_list.get((i,))
            if s=='':
                break
            if s==room_name:
                self.room_list.delete(i,i)
                break
            i+=1

    def newroom(self, room_name):
        if room_name.startswith('&'):
            _,u,v = room_name.split('&')
            if u == self.usr_name:
                x = v
            else:
                x = u
            self.friend_list.insert(END, x)
        else:
            self.room_list.insert(END, room_name)

    def leave(self, room_name):
        self.tl.destroy()
        self.UI.session.leave_room(self.usr_name, room_name)
        self.UI.rooms.pop(room_name)
    



if __name__ == '__main__':
    HOST = '127.0.0.1'
    PORT = 8080
    x = ChatroomUI(ClientSession(HOST, PORT), '233')
    x.tk.mainloop()
