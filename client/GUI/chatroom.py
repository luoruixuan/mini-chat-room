from tkinter import *

class ChatroomUI:
    def __init__(self, usr_name, **args):
        self.usr_name = usr_name
        tk = Tk()
        self.tk = tk
        ft = font.Font(family='Times New Roman', size=15)
        self.ft = ft
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
            lst = get_friend_list(self.usr_name)
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
        status, msg = send_friend_request_to_server(self.usr_name, friend_name, vm)
        if status:
            messagebox.showinfo('Succeed', msg)
            tl.destroy()
        else:
            messagebox.showerror('Fail', msg)

    def ShowChatRooms(self):
        try:
            assert self.chatrooms.winfo_exists()==1
        except:
            lst = get_chat_rooms(self.usr_name)
            cr = Toplevel(self.tk)
            self.chatrooms = cr
            cr.title('Chat room list')
            t = Canvas(cr)
            bar = Scrollbar(cr)
            bar.config(command=t.yview)
            t.config(yscrollcommand=bar.set,height=20+60*len(lst),width=200)
            for i, name in enumerate(lst):
                Button(t, text=name, font=self.ft, command=lambda:self.OpenChatRoom(name)).place(y=20+i*60,x=20)
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
        status, msg = send_enter_chat_room_request_to_server(self.usr_name, roomID, password)
        if status:
            messagebox.showinfo('Succeed', msg)
            tl.destroy()
        else:
            messagebox.showerror('Fail', msg)

    def CreateChatRoom(self):
        status, msg = send_create_chat_room_to_server(self.usr_name)
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
    def OpenChatRoom(self, name):
        pass
    

# TODO
def get_friend_list(name):
    return ['Alice', 'Bob', 'Carol']

# TODO
def get_chat_rooms(name):
    return ['aaa', 'bbb', 'ccc','d','e','f']

# TODO
def send_friend_request_to_server(usr_name, friend_name, ver_msg):
    return True, 'Succeed'

# TODO
def send_create_chat_room_to_server(usr_name):
    return True, 'Succeed'

# TODO
def send_enter_chat_room_request_to_server(usr_name, room_id, password):
    return True, 'Succeed'

if __name__ == '__main__':
    x = ChatroomUI('233')
    x.tk.mainloop()
