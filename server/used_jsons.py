# -*- coding: utf-8 -*-

# 命令json(dict)

# 传输RSA公钥
{'type': 'init',
 'msg': 'RSApubKey',
 'Key': ''
 }
# 接收AES密钥
{'type': 'init',
 'msg': 'AESKey',
 'Key': ''
 }

# 登录
{'type': 'command',
 'msg': 'login',
 'usr_name': 'lrx',
 'password': 'lrx',
 'timestamp': 1530000000}
# response
{'type': 'server_response',
 'status': True,  # False 表示操作成功或失败
 'msg': 'Succeed.',  # 'Password error.'
 'info': ''
 }

# 注册
{'type': 'command',
 'msg': 'register',
 'usr_name': 'lrx',
 'password': 'lrx',
 'timestamp': 1530000000}
# response
{'type': 'server_response',
 'status': True,
 'msg': 'Succeed.',
 'info': ''
 }

# 登出
{'type': 'command',
 'msg': 'logout',
 'usr_name': 'lrx',
 'timestamp': 1530000000}
# response
{'type': 'server_response',
 'status': True,
 'msg': 'Succeed.',
 'info': ''
 }

# 修改密码
{'type': 'command',
 'msg': 'change_password',
 'usr_name': 'lrx',
 'old_password': '123456',
 'new_password': '654321',
 'timestamp': 1530000000}
# response
{'type': 'server_response',
 'status': True,  # False
 'msg': 'Succeed.',
 'info': ''
 }

# 创建群
{'type': 'command',
 'msg': 'create_group',
 'usr_name': 'lrx',
 'group_name': 'group1',
 'timestamp': 1530000000}
# response
{'type': 'server_response',
 'status': True,
 'msg': 'Succeed.',
 'info': ''
 }

# 群主踢人
{'type': 'command',
 'msg': 'remove_person',
 'usr_name': 'lrx',
 'friend_name': 'wy',
 'group_name': 'group1',
 'timestamp': 1530000000}
# response
{'type': 'server_response',
 'status': True,
 'msg': 'Succeed.'
 }
# 1、creator, creator:
# 向群内所有人发
{'type': 'usr_removed',
 'group_name': 'group1',
 'msg': 'You are removed from group1'
 }
# 2、creator/X, X:
# 向X发
{'type': 'usr_removed',
 'group_name': 'group1',
 'msg': 'You are removed from group1'
 }
# 向群内其它人发
{'type': 'person_out',
 'group_name': 'group1',
 'usr_name': 'X'
 }

# 查看群信息
{'type': 'command',
 'msg': 'desc_group',
 'usr_name': 'lrx',
 'group_name': 'group1',
 'timestamp': 1530000000}
# response
{'type': 'server_response',
 'status': True,
 'msg': 'Succeed.',
 'info': {'creator': 'lrx',
          'group_name': 'group1',
          'members': ['wy', 'lrx', 'ly', 'qwt'],
          'files': ['a.txt', 'b.jpg'],
          'history': ['lrx: hello!\nwy: hello.\n']
          }
 }
history = [{}, {}, {}, {}]  # 如下
{
    'group_name': 'group1',
    'usr_name': 'lrx',
    'message': 'hello world',
    'date_time': '2010-01-01 12:00:00'
}

# 消息
# 在群内说话
{'type': 'group_message',
 'msg': '在群内说话',
 'usr_name': 'lrx',
 'group_name': 'group1',
 'timestamp': 1530000000}
# response
{'type': 'server_response',
 'status': True,
 'msg': 'Succeed.',
 'info': ''
 }
# 成功时给其他人
{'type': 'person_speak',
 'group_name': 'group1',
 'usr_name': 'lrx',
 'message': 'hello world',
 'date_time': '2010-01-01 12:00:00'
 }

# 加好友请求
{'type': 'command',
 'msg': 'add_friend',
 'usr_name': 'lrx',
 'friend_name': 'wy',
 'verification_message': 'hello',
 'timestamp': 1530000000}
# response
{'type': 'server_response',
 'status': True,
 'msg': 'Succeed.'
 }

# 查看收到的请求
{'type': 'command',
 'msg': 'get_verification_message',
 'usr_name': 'lrx',
 'timestamp': 1530000000}
# response
{'type': 'server_response',
 'status': True,
 'msg': 'Succeed.',
 'info': {'wy': 'hello', 'ly': 'hi', 'qwt': 'Hi'}
 }

# 接受或拒绝请求
{'type': 'command',
 'msg': 'add_friend_response',
 'usr_name': 'lrx',
 'friend_name': 'wy',
 'accept': True,
 'timestamp': 1530000000}
# response
{'type': 'server_response',
 'status': True,
 'msg': 'Succeed.'
 }

# 邀请好友进群
{'type': 'command',
 'msg': 'invite_friend',
 'usr_name': 'lrx',
 'friend_name': 'wy',
 'group_name': 'group1',
 'timestamp': 1530000000}
# response
{'type': 'server_response',
 'status': True,
 'msg': 'Succeed.'
 }
# 给被邀请人发
{'type': 'usr_invited',
 'group_name': 'group1',
 'msg': 'You are invited into group1'
 }

# 查询用户所在群列表
{'type': 'command',
 'msg': 'get_group_list',
 'usr_name': 'lrx',
 'timestamp': 1530000000}
# response
{'type': 'server_response',
 'status': True,
 'msg': 'Succeed.',
 'info': ['group1', 'group2']
 }

# 查询用户好友列表
{'type': 'command',
 'msg': 'get_friend_list',
 'usr_name': 'lrx',
 'timestamp': 1530000000}
# response
{'type': 'server_response',
 'status': True,
 'msg': 'Succeed.',
 'info': ['wy', 'ly', 'qwt']
 }
