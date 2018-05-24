from client_session import ClientSession
import sys
sys.path.append('GUI')
from login import LoginUI

# with open('config.txt') as f:
#     l = f.readlines()
#     HOST, PORT = l[0].strip(), int(l[1].strip())
#     LoginUI(ClientSession(HOST, PORT)).tk.mainloop()
LoginUI(ClientSession('127.0.0.1', 8080)).tk.mainloop()
