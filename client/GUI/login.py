from tkinter import *

class LoginUI:
    def __init__(self):
        tk = Tk()
        self.tk = tk
        ft = font.Font(family='Times New Roman', size=16)
        tk.title('login')
        width, height = 500, 400
        tk.minsize(width, height)
        tk.maxsize(width, height)
        tk.geometry('%dx%d+%d+%d' % (width,height,(tk.winfo_screenwidth() - width ) / 2, (tk.winfo_screenheight() - height) / 2))
        Label(tk, text='User name: ', font=ft).place(x=50, y=150)
        Label(tk, text='Password: ', font=ft).place(x=50, y=190)
        
        var_usr_name = StringVar()
        var_usr_name.set('user name')
        entry_usr_name = Entry(tk, textvariable=var_usr_name, font=ft)
        entry_usr_name.place(x=190, y=150)
        self.entry_usr_name = entry_usr_name
        var_usr_pwd = StringVar()
        entry_usr_pwd = Entry(tk, textvariable=var_usr_pwd, show='*', font=ft)
        entry_usr_pwd.place(x=190, y=190)
        self.entry_usr_pwd = entry_usr_pwd

        but_login = Button(tk, text='login', font=ft, command=lambda:LoginUI.login(self))
        but_login.place(x=90, y=240)

        but_signup = Button(tk, text='sign up', font=ft, command=lambda:LoginUI.signup(self))
        but_signup.place(x=230, y=240)

        tk.mainloop()


    def login(self):
        print('login')
        pass

    def signup(self):
        print('sign up')
        pass


if __name__ == '__main__':
    LoginUI()
