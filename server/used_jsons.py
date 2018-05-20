# -*- coding: utf-8 -*-

# 命令json(dict)
# 登陆
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
# {'type': 'command',
#  'msg': 'register',
#  'usr_name': 'lrx',
#  'password': 'lrx',
#  'timestamp': 1530000000}

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

# 进入群
{'type': 'command',
 'msg': 'enter_group',
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
{'type': 'person_in',
 'group_name': 'group1',
 'usr_name': 'lrx'
 }

# 离开群
{'type': 'command',
 'msg': 'leave_group',
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
{'type': 'person_out',
 'group_name': 'group1',
 'usr_name': 'lrx'
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
          'members': ['wy', 'lrx', 'ly', 'qwt']}
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
 'message': 'hello world'
 }
