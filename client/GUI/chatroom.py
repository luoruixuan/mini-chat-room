from tkinter import *
from tkinter import filedialog
import sys
import os
sys.path.append('..')
from client_session import *

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
        try:
            js = self.session.queue.get_nowait()
            self.msg_func(js)
        except:
            pass
        self.tk.after(500, self.loop)

    def msg_func(self, js):
        print('&')
        if js['type'] == 'person_speak':
            room_name = js['group_name']
            self.main_part.recv_msg(room_name, js['usr_name']+': '+js['message'])
        elif js['type'] == 'person_in':
            room_name = js['group_name']
            self.main_part.person_in(room_name, js['usr_name'])
        elif js['type'] == 'person_out':
            room_name = js['group_name']
            self.main_part.person_out(room_name, js['usr_name'])
        elif js['type'] == 'person_share_file':
            room_name = js['group_name']
            self.main_part.get_file(room_name, js)

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
    def create_chat_room_request(self, RN, PW, tl):
        room_name , password = RN.get(), PW.get()
        status, msg = self.session.create_chat_room_request(self.usr_name, room_name, password)
        if status:
            messagebox.showinfo('Succeed', msg)
            tl.destroy()
            self.OpenChatRoom(room_name)
        else:
            messagebox.showerror('Fail', msg)
            
    # TODO
    def ShowMessages(self):
        pass

    # TODO
    def ShowSetting(self):
        pass
    
    def OpenChatRoom(self, room_name):
        status, info = self.session.get_room_info(self.usr_name, room_name)
        if not status:
            messagebox.showerror('Fail', info)
            return
        self.rooms[room_name] = Room(self, info)

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
        width, height = 1000, 800
        tl.minsize(width, height)
        #tl.maxsize(width, height)
        self.tl = tl
        # 房间信息、房主设置
        row = Frame(tl)
        #row.pack()
        Label(row, text='User name: '+self.usr_name, font=self.ft).place(relx=0.1, rely=0., relwidth=0.2, relheight=1.)
        self.RN = Label(row, text='Room name: '+room_name, font=self.ft)
        self.RN.place(relx=0.4, rely=0., relwidth=0.2, relheight=1.)
        setting_act = lambda:self.chat_room_setting()
        Button(row, text='Setting', font=self.ft, command=setting_act).place(relx=0.7, rely=0., relwidth=0.2, relheight=1.)
        row.place(relx=0., rely=0., relwidth=1., relheight=0.1)

        # 输入框
        row = Frame(tl)
        input_box = Text(row, font=self.ft)
        input_box.place(relx=0., rely=0., relwidth=0.62, relheight=0.95)
        self.input_box = input_box

        but_sd = Button(row, text='send', font=self.ft, command=lambda:self.send_msg())
        but_sd.place(relx=0.64, rely=0.3, relwidth=0.1, relheight=0.6)

        but_cl = Button(row, text='clear', font=self.ft, command=lambda:self.clear_msg())
        but_cl.place(relx=0.76, rely=0.3, relwidth=0.1, relheight=0.6)

        but_sf = Button(row, text = 'File', font = self.ft, command=lambda:self.share_file(room_name))
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
        self.UI.session.enter_chat_room_request(self.usr_name, rn, '')
        self.flush_room(rn)

    def click_friend(self):
        lb = self.friend_list
        try:
            fn = lb.get(lb.curselection())
        except:
            return
        # TODO 好友是否视为二人群？
        self.flush_room(fn)

    def chat_room_setting(self):
        if self.room_name == 'Hall':
            messagebox.showerror('Fail', 'Please enter a room first.')
            return
        info = self.all_rooms[self.room_name]
        if self.usr_name != info['creator']:
            messagebox.showerror('Fail', 'You are not the creator of the room.')
            return
        # TODO room setting part

    def clear_input_box(self):
        self.input_box.delete(0.0,END)

    def flush_list(self):
        # TODO 获取用户的群列表
        lst = ['1', '2', '3', '4']
        for n in lst:
            self.room_list.insert(END, n)

        # TODO 获取用户好友列表
        lst = ['lrx', 'wy', 'ly', 'qwt']
        for n in lst:
            self.friend_list.insert(END, n)

    # 进入房间时初始化
    def flush_room(self, room_name):
        if not room_name in self.all_rooms:
            status, info = self.UI.session.get_room_info(self.usr_name, room_name)
            if not status:
                messagebox.showerror('Fail', info)
                return
            self.all_rooms[room_name] = info
            # debug
            info['files']=['a.txt', 'b.jpg']
            info['history']='123'
        self.room_name = room_name
        self.RN.configure(text='Room name: '+room_name)
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
        self.recv_msg(self.room_name, info['history'])

    def share_file(self, room_name):
        file_name = filedialog.askopenfilename()
        if not file_name:
            return
        f = open(file_name, 'r')
        file_content = f.read()
        f.close()
        file_name = file_name.split('/')[-1]
        status, msg = self.UI.session.share_file(room_name, file_name, file_content)
        if not status:
            messagebox.showerror('Fail', msg)

    def get_file(self, js):
        user_name = js['usr_name']
        file_name = js['file_name']
        file_content = js['file_content']
        file_dir = os.getcwd()
        f = open(file_dir+'/'+file_name, 'w')
        f.write(file_content)
        f.close()
        self.recv_msg('你收到了来自' + user_name + '的文件（%s）' % file_name+',存放在了%s下'%file_dir)

    def download_file(self):
        # TODO 文件下载
        lb = self.file_listbox
        try:
            fn = lb.get(lb.curselection())
        except:
            return
        print('Downloading %s:'%fn)

    def send_msg(self):
        room_name = self.room_name
        box = self.input_box
        if room_name == 'Hall':
            messagebox.showerror('Fail', 'Please enter a room first.')
            return
        msg = box.get(0.0, END)[:-1]
        self.recv_msg(room_name, self.usr_name+': '+msg)
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

    def leave(self, room_name):
        self.tl.destroy()
        self.UI.session.leave_room(self.usr_name, room_name)
        self.UI.rooms.pop(room_name)
    



if __name__ == '__main__':
    HOST = '127.0.0.1'
    PORT = 8080
    x = ChatroomUI(ClientSession(HOST, PORT), '233')
    x.tk.mainloop()
