import pymssql

usercount=4 #用于添加用户时的userid
#连接数据库的服务器ip、端口、数据库名
hostip='localhost'
portnum='51046'
DB='ChatMembers2018' 

# 用户的查找、添加、删除
class UserOperations:
    state=0
    def __init__(self):
        pass
    def query(self,username,userpwd='',para=0):
        '''
        username: str
        userpwd: str
        para: 0:用户名和密码查询，用于登陆时查找
              1：用户名查询，仅查找此用户是否存在
        返回值：userid：正常， -1：无此用户， -2：密码错误
        '''
        conn =pymssql.connect(host= hostip,port=portnum,database=DB)
        cursor=conn.cursor()    #游标
        cursor.execute('SELECT * FROM Users.User_Info as U WHERE U.Username=%s', username)
        row=cursor.fetchone()
        if row:
            if para==0 and row[2]==userpwd:
                state=row[0]    #赋值userid
            elif para==0 and row[2]!=userpwd:
                state=-2    #密码错
            elif para==1:
                state=row[0]    #赋值userid
        else:
            state =-1    #无用户
        cursor.close()
        conn.close()
        return state
    def add(self, username, userpwd):
        global usercount
        uid=self.query(username=username,para=1)
        if uid!=-1: #此用户已存在
            return -1
        conn =pymssql.connect(host= hostip,port=portnum,database=DB)
        cursor=conn.cursor()    #游标
        sql='INSERT INTO Users.User_Info(Userid,Username,UserPassword) Values(%d,%s,%s)'
        try:
            cursor.execute(sql,(usercount, username, userpwd))
            conn.commit()
            usercount=usercount+1
        except:
            conn.rollback()
            conn.close()
            return -1
        conn.close()
        return 0
        
    def remove(self, username, userpwd):
        #返回值：0正常，-1用户不存在或者密码错
        querystate=self.query(username,userpwd)
        if querystate<0:    #无此用户
            return -1
        else:
            conn =pymssql.connect(host= hostip,port=portnum,database=DB)
            cursor=conn.cursor()
            try:
                cursor.execute('DELETE FROM Users.User_Info Where Username=%s \
                            and UserPassWord=%s',(username, userpwd))
                conn.commit()
            except:
                conn.rollback()
                conn.close()
                return -1
            cursor.close()
            conn.close()
            return 0
        

# 在线用户的添加和移除
class UserOnline:
    state=0
    def __init__(self):
        pass

    def query(self,username='',userid=-1):
        '''
        userid:查询时如果已知userid可以直接用这个
        username: 查询时不知道userid可以用用户名查找
        返回值：0在线， -1：不在线，-2：错误，即无此用户
        '''
        if userid==-1:
            Userquery=UserOperations()
            userid=Userquery.query(username=username,para=1)
            if userid==-1:  #查无此用户
                state=-2
                return state
        conn =pymssql.connect(host= hostip,port=portnum,database=DB)
        cursor=conn.cursor()    #游标
        sql="SELECT Userid FROM Users.Online as U WHERE U.Userid=%d"
        cursor.execute(sql, userid)
        row = cursor.fetchone()
        if row:
            state=0 #在线
        else:
            state =-1 #不在线
        cursor.close()
        conn.close()
        return state

    def add(self,username='',userid=-1):
        '''
        #,IP_addr=''
        userid:添加时如果已知userid可以直接用这个
        username: 不知道userid可以用用户名查找，然后再添加
        return :0:正常， -1：无此用户
        '''
        if userid==-1:
            Userquery=UserOperations()
            userid=Userquery.query(username=username,para=1)
            if userid==-1:  #查无此用户
                state=-1
                return state
        conn =pymssql.connect(host= hostip,port=portnum,database=DB)
        cursor=conn.cursor()    #游标
        try:
            sql='Insert Users.Online(userid) values(%d)'
            cursor.execute(sql,(userid))
            conn.commit()
        except:
            conn.rollback()
            conn.close()
            return -2
        conn.close()
        return 0
        
    def remove(self, username='', userid=-1):
        '''
        userid:删除时如果已知userid可以直接用这个
        username: 不知道userid可以用用户名查找，然后再删除
        return :0:正常， -1：无此用户
        '''
        if userid==-1:
            Userquery=UserOperations()
            userid=Userquery.query(username=username,para=1)
            if userid==-1:  #查无此用户
                state=-1
                return state
        conn =pymssql.connect(host= hostip,port=portnum,database=DB)
        cursor=conn.cursor()
        try:
            cursor.execute('DELETE FROM Users.Online Where Userid=%d',userid)
            conn.commit()
        except:
            conn.rollback()
            conn.close()
            return -1
        cursor.close()
        conn.close()
        return 0

# 查询\添加\删除好友
class UserFriends:
    state=0
    def __init__(self, username):
        self.username = username 
    
    def add(self, friendname):
        #返回值：0添加成功，-1：这个friend用户不存在
        Uquery=UserOperations()
        uid1=Uquery.query(username=self.username,para=1)
        uid2=Uquery.query(username=friendname,para=1)
        if uid2==-1:
            state=-1
            return state
        conn =pymssql.connect(host= hostip,port=portnum,database=DB)
        cursor=conn.cursor()
        sql='INSERT INTO Users.Friends(Userid1,Userid2) Values(%d,%d)'
        try:
            cursor.execute(sql,(uid1,uid2))
            conn.commit()
        except:
            conn.rollback()
        conn.close()
        return 0
    
    def remove(self, friendname):
        #返回值：0删除成功，-1：这个friend用户不存在
        Uquery=UserOperations()
        uid1=Uquery.query(username=self.username,para=1)
        uid2=Uquery.query(username=friendname,para=1)
        if uid2==-1:
            return -1
        conn =pymssql.connect(host= hostip,port=portnum,database=DB)
        cursor=conn.cursor()
        try:
            cursor.execute('Delete From Users.Friends Where (Userid1=%d and Userid2=%d) or \
                        (Userid1=%d and Userid2=%d)',(uid1,uid2,uid2,uid1))
            conn.commit()
        except:
            conn.rollback()
        cursor.close()
        conn.close()
        return 0

    def queryFriendList(self,friendlist):
        # 返回对象的好友列表
        Uquery=UserOperations()
        uid1=Uquery.query(username=self.username,para=1)
        
        conn =pymssql.connect(host= hostip,port=portnum,database=DB)
        cursor=conn.cursor()
        sql='Select distinct Username \
            from Users.User_Info T1,(Select * From Users.Friends Where Userid1=%d or Userid2=%d)T2\
            Where T1.Userid=T2.Userid1 or T1.Userid=T2.Userid2'
        cursor.execute(sql,(uid1,uid1))
        results=cursor.fetchall()
        for row in results:
            if row[0]!=self.username:
                friendlist.append(row[0])
            
# 创建群聊
# 加入群聊
groupid=1
class ChatGroup:
    def __init__(self,username):
        self.username=username
        sql1='Select Userid From Users.User_Info Where Username=%s'
        conn=pymssql.connect(host= hostip,port=portnum,database=DB)
        cursor=conn.cursor()
        cursor.execute(sql1,self.username)
        row=cursor.fetchone()
        if row:
            self.userid=row[0]
        else:
            self.userid=-1
        conn.close()

    def CreateGroup(self,groupname=''):
        #user create a new group
        #return :0 成功，-1：username用户不存在,-2:groupname 这个组已存在
        global groupid
        conn=pymssql.connect(host= hostip,port=portnum,database=DB)
        cursor=conn.cursor()
        sql2='Insert Into Users.Chatgroup(Groupid,Groupname,GroupOwner) Values(%d,%s,%d)'
        if self.userid!=-1:
            tmp=self.OpenGroup(groupname)
            if tmp!=-2: #这个组已经存在了
                conn.close()
                return -2
            try:
                cursor.execute(sql2,(groupid,groupname,self.userid))
                conn.commit()
                self.groupid=groupid    #保存
                self.groupOwner=self.userid
                self.groupname=groupname
                groupid=groupid+1
                self.addGroupMem(self.username)  #把群主加入群
            except:
                conn.rollback()
                conn.close()
                return -2

            conn.close()
            return 0
        else:
            conn.close()
            return -1
    def OpenGroup(self,groupname):
        #参数：username：分为成员和群主两种，groupname：群聊名称
        #返回值：0正常，-1：不存在此用户username，-2：不存在这个组有成员username
        conn=pymssql.connect(host= hostip,port=portnum,database=DB)
        cursor=conn.cursor()
        sql2='Select G.Groupid, GroupOwner \
                From Users.Chatgroup as G inner join Users.ChatgroupMem as GM \
                    on G.Groupid=GM.Groupid \
                Where G.Groupname=%s and GM.Memid=%d '
        if self.userid!=-1:
            cursor.execute(sql2,(groupname,self.userid))
            result=cursor.fetchone()
            if result:
                self.groupid=result[0]
                self.groupOwner=result[1]
                self.groupname=groupname
                conn.close()
                return 0
            else:
                conn.close()
                return -2
        else:
            conn.close()
            return -1
    def addGroupMem(self,Memname):
        #返回值：0正常，-1：不存在此用户Memname,-2:群聊已存在此成员
        conn=pymssql.connect(host= hostip,port=portnum,database=DB)
        cursor=conn.cursor()
        sql1='Select Userid From Users.User_Info Where Username=%s'
        sql2='Select Memid From Users.ChatgroupMem Where Groupid=%d and Memid=%d'
        sql3='Insert Into Users.ChatgroupMem(Memid,Groupid) Values(%d,%d)'
        cursor.execute(sql1,Memname)
        row=cursor.fetchone()   #Memid
        if row:
            cursor.execute(sql2,(self.groupid,row[0]))
            result=cursor.fetchone()
            if result:  #已存在此成员
                conn.close()
                return -2
            try:
                cursor.execute(sql3,(row[0],self.groupid))
                conn.commit()
            except:
                conn.rollback()
            conn.close()
            return 0
        else:
            conn.close()
            return -1
    def removeMem(self,Memname):
        #参数: Memname：被踢出的成员
        #注意：self.username是群主或者等于Memname时才有权力执行，当群主踢出群主时相当于解散群
        #返回值:0成功， -1：失败
        conn=pymssql.connect(host= hostip,port=portnum,database=DB)
        cursor=conn.cursor()
        sql1='Select * From Users.User_Info Where Username=%s or Username=%s'
        sql2='Delete From Users.ChatgroupMem Where Groupid=%d'
        sql3='Delete From Users.Chatgroup Where Groupid=%d'
        sql4='Delete From Users.ChatgroupMem Where Groupid=%d and Memid=%d'
        cursor.execute(sql1,(self.username,Memname))
        results=cursor.fetchall()
        for row in results:
            if row[1]==self.username:
                executorid=row[0]
            elif row[1]==Memname:
                RemoveMemid=row[0]
        if self.groupOwner==executorid:
            if self.groupOwner==RemoveMemid:    #解散群
                try:
                    cursor.execute(sql2,self.groupid)
                    cursor.execute(sql3,self.groupid)
                    conn.commit()
                except:
                    conn.rollback()
                conn.close()
            else:   #删除群成员Memname
                try:
                    cursor.execute(sql4,(self.groupid,RemoveMemid))
                    conn.commit()
                except:
                    conn.rollback()
                conn.close()
            return 0
        elif executorid==RemoveMemid:   #Memname退出群
            try:
                cursor.execute(sql4,(self.groupid,RemoveMemid))
                conn.commit()
            except:
                conn.rollback()
            conn.close()
            return 0

        else:   #无权限
            return -1
    def queryChatGroupList(self,ChatGroupList):
        #参数：传入一个List
        #返回值：0正常，-1：此用户不存在
        conn=pymssql.connect(host= hostip,port=portnum,database=DB)
        cursor=conn.cursor()
        sql1='Select * From Users.User_Info Where Username=%s'
        sql2='Select Groupname \
                From Users.Chatgroup as G inner join Users.ChatgroupMem as GM \
                    on G.Groupid=GM.Groupid \
                Where GM.Memid=%d '
        cursor.execute(sql1,self.username)
        row =cursor.fetchone()
        if row:
            userid=row[0]
            cursor.execute(sql2,userid)
            results=cursor.fetchall()
            for onerow in results:
                ChatGroupList.append(onerow[0])
            conn.close()
            return 0
        else:
            return -1


# 消息
