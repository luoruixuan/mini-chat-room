from tkinter import *
import sys
sys.path.append('..')
from client_session import *

class ChatroomUI:
    def __init__(self, session, usr_name, **args):
        self.session = session
        self.session.msg_func = lambda:self.msg_func
        self.usr_name = usr_name
        self.rooms = {}
        tk = Tk()
        self.tk = tk
        # 默认字体
        ft = font.Font(family='Times New Roman', size=15)
        self.ft = ft

        # 主界面
        tk.title('Main')
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
        self.friendlist = None
        self.chatrooms = None

    def msg_func(self, js):
        cid = js['ID']
        if cid in rooms:
            self.rooms[cid].recv_msg(js['message'])

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
        Label(tl, text='Room ID: ', font=self.ft).place(x=50, y=150)
        Label(tl, text='Password: ', font=self.ft).place(x=50, y=190)
        
        var_usr_name = StringVar()
        entry_usr_name = Entry(tl, textvariable=var_usr_name, font=self.ft)
        entry_usr_name.place(x=200, y=150)
        self.entry_usr_name = entry_usr_name
        var_vm = StringVar()
        entry_vm = Entry(tl, textvariable=var_vm, font=self.ft)
        entry_vm.place(x=200, y=190)
        self.entry_vm = entry_vm

        but_sd = Button(tl, text='send', font=self.ft, command=lambda:self.send_enter_chat_room_request(tl))
        but_sd.place(x=170, y=240)
    def send_enter_chat_room_request(self, tl):
        roomID = self.entry_usr_name.get()
        password = self.entry_vm.get()
        status, msg = self.session.enter_chat_room_request(self.usr_name, roomID, password)
        if status:
            messagebox.showinfo('Succeed', msg)
            tl.destroy()
        else:
            messagebox.showerror('Fail', msg)

    def CreateChatRoom(self):
        status, msg = self.session.create_chat_room_request(self.usr_name)
        if status:
            messagebox.showinfo('Succeed', msg)
        else:
            messagebox.showerror('Fail', msg)
            
    # TODO
    def ShowMessages(self):
        pass

    # TODO
    def ShowSetting(self):
        pass
    
    # TODO
    def OpenChatRoom(self, cid):
        status, info = self.session.get_room_info(cid)
        if not status:
            messagebox.showerror('Fail', info)
            return
        self.rooms[cid] = Room(self, info)

class Room:
    def __init__(self, UI, info):
        self.UI = UI
        self.tk = UI.tk
        self.usr_name = UI.usr_name
        self.info = info
        self.ft = UI.ft
        cid = info['ID']
        tl = Toplevel(self.tk)
        tl.title('Chat room %d'%cid)
        width, height = 500, 400
        tl.minsize(width, height)
        tl.maxsize(width, height)
        # 房间信息、房主设置
        row = Frame(tl)
        row.pack()
        Label(row, text='Room ID: '+str(cid), font=self.ft).pack(side=LEFT, padx=15)
        Label(row, text='Room name: '+info['name'], font=self.ft).pack(side=LEFT, padx=15)
        setting_act = lambda:self.chat_room_setting(info)
        if self.usr_name != info['creator']:
            setting_act = lambda:messagebox.showerror('Fail', 'You are not the creator of the room.')
        Button(row, text='Setting', font=self.ft, command=setting_act).pack(side=LEFT, padx=15)

        # 输入框
        row = Frame(tl)
        row.pack(side=BOTTOM, pady=10)
        input_box = Entry(row, font=self.ft)
        input_box.pack(side=LEFT, padx=15)

        but_sd = Button(row, text='send', font=self.ft, command=lambda:self.send_msg(cid, input_box))
        but_sd.pack(side=LEFT, padx=15)

        but_cl = Button(row, text='clear', font=self.ft, command=lambda:self.clear_msg())
        but_cl.pack(side=LEFT, padx=15)

        # 消息框
        row = Frame(tl)
        row.pack(expand='yes', padx=15)
        t = Text(row, borderwidth=0, font=self.ft)
        bar = Scrollbar(row)
        bar.config(command=t.yview)
        t.config(yscrollcommand=bar.set)
        bar.pack(side=RIGHT,fill=Y)
        t.pack(expand='yes', anchor='nw')
        t['state']='disabled'
        hist_box = t
        self.hist_box = hist_box
        
    def send_msg(self, cid, box):
        msg = box.get()
        status, msg = self.UI.session.send_msg(cid, msg)
        if not status:
            messagebox.showerror('Fail', msg)
            return
        box.delete(0, END)
    def clear_msg(self):
        self.hist_box['state']='normal'
        self.hist_box.delete(0.0, END)
        self.hist_box['state']='disabled'

    def recv_msg(self, msg):
        self.hist_box['state']='normal'
        self.hist_box.insert(END, str(msg)+'\n')
        self.hist_box['state']='disabled'
    



if __name__ == '__main__':
    HOST = '127.0.0.1'
    PORT = 8080
    x = ChatroomUI(ClientSession(HOST, PORT), '233')
    x.tk.mainloop()
