from tkinter import *
#import sys
#sys.path.append('..')
from client_session import *
from chatroom import ChatroomUI

HOST = '127.0.0.1'
PORT = 8080

class LoginUI:
    def __init__(self, session):
        tk = Tk()
        self.tk = tk
        self.session = session
        ft = font.Font(family='Times New Roman', size=16)
        tk.title('login')
        width, height = 500, 400
        tk.minsize(width, height)
        tk.maxsize(width, height)
        tk.geometry('%dx%d+%d+%d' % (width,height,(tk.winfo_screenwidth() - width ) / 2, (tk.winfo_screenheight() - height) / 2))
        Label(tk, text='User name: ', font=ft).place(x=50, y=150)
        Label(tk, text='Password: ', font=ft).place(x=50, y=190)
        
        var_usr_name = StringVar()
        entry_usr_name = Entry(tk, textvariable=var_usr_name, font=ft)
        entry_usr_name.place(x=190, y=150)
        self.entry_usr_name = entry_usr_name
        var_usr_pwd = StringVar()
        entry_usr_pwd = Entry(tk, textvariable=var_usr_pwd, show='*', font=ft)
        entry_usr_pwd.place(x=190, y=190)
        self.entry_usr_pwd = entry_usr_pwd

        but_login = Button(tk, text='login', font=ft, command=lambda:self.login())
        but_login.place(x=90, y=240)

        but_signup = Button(tk, text='sign up', font=ft, command=lambda:self.signup())
        but_signup.place(x=230, y=240)



    def login(self):
        usr_name = self.entry_usr_name.get()
        pwd = self.entry_usr_pwd.get()
        status, msg = self.session.login(usr_name, pwd)
        if not status:
            messagebox.showerror('Fail', msg)
            return
        self.tk.destroy()
        ChatroomUI(self.session, usr_name=usr_name)
        

    def signup(self):
        self.tk.destroy()
        RegisterUI(self.session)

class RegisterUI:
    def __init__(self, session):
        tk = Tk()
        self.tk = tk
        self.session = session
        ft = font.Font(family='Times New Roman', size=15)
        tk.title('register')
        width, height = 500, 400
        tk.minsize(width, height)
        tk.maxsize(width, height)
        tk.geometry('%dx%d+%d+%d' % (width,height,(tk.winfo_screenwidth() - width ) / 2, (tk.winfo_screenheight() - height) / 2))
        Label(tk, text='User name: ', font=ft).place(x=50, y=150)
        Label(tk, text='Password: ', font=ft).place(x=50, y=190)
        Label(tk, text='Confirm password: ', font=ft).place(x=50, y=230)
        
        var_usr_name = StringVar()
        entry_usr_name = Entry(tk, textvariable=var_usr_name, font=ft)
        entry_usr_name.place(x=230, y=150)
        self.entry_usr_name = entry_usr_name
        var_usr_pwd = StringVar()
        entry_usr_pwd = Entry(tk, textvariable=var_usr_pwd, show='*', font=ft)
        entry_usr_pwd.place(x=230, y=190)
        self.entry_usr_pwd = entry_usr_pwd
        var_usr_pwd_c = StringVar()
        entry_usr_pwd_c = Entry(tk, textvariable=var_usr_pwd_c, show='*', font=ft)
        entry_usr_pwd_c.place(x=230, y=230)
        self.entry_usr_pwd_c = entry_usr_pwd_c

        but_login = Button(tk, text='login', font=ft, command=lambda:self.login())
        but_login.place(x=230, y=280)

        but_register = Button(tk, text='register', font=ft, command=lambda:self.register())
        but_register.place(x=90, y=280)



    def login(self):
        self.tk.destroy()
        LoginUI(self.session)

    def register(self):
        usr_name = self.entry_usr_name.get()
        pwd = self.entry_usr_pwd.get()
        pwd_c = self.entry_usr_pwd_c.get()
        if pwd != pwd_c:
            messagebox.showerror('Error', 'Password does not match.')
            return
        
        status, msg = self.session.register(usr_name, pwd)
        if not status:
            messagebox.showerror('Fail', msg)
            return
        messagebox.showinfo('Succeed', msg)
        self.login()
        

if __name__ == '__main__':
    HOST = '127.0.0.1'
    PORT = 8080
    LoginUI(ClientSession(HOST, PORT)).tk.mainloop()
