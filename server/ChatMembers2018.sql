---------------------------------------------------------------------
-- Create Database
---------------------------------------------------------------------

-- USE master;
USE master;

-- Drop database
IF DB_ID('ChatMembers2018') IS NOT NULL DROP DATABASE ChatMembers2018;

-- If database could not be created due to open connections, abort
IF @@ERROR = 3702 
   RAISERROR('Database cannot be dropped because there are still open connections.', 127, 127) WITH NOWAIT, LOG;

-- Create database
CREATE DATABASE ChatMembers2018;
GO

USE ChatMembers2018;
GO

---------------------------------------------------------------------
-- Create Schemas
---------------------------------------------------------------------

CREATE SCHEMA Administrator AUTHORIZATION dbo;
GO
CREATE SCHEMA Users AUTHORIZATION dbo;
GO
---------------------------------------------------------------------
-- create tables
---------------------------------------------------------------------

---------------------------------------------------------------------
---------------------------------------------------------------------
Create Table Administrator.Mem_Info
(
	Memid INT NOT NULL identity(1,1) Primary Key,
	Memname VARCHAR(40) NOT NULL Unique,
	MemPassword VARCHAR(20) NOT NULL
)
---------------------------------------------------------------------
-- userid: from 0 to ...
-- username: N'lrx'
-- userPassword: N'123456'
---------------------------------------------------------------------
Create Table Users.User_Info
(
	Userid INT NOT NULL identity(1,1) Primary Key,
	Username VARCHAR(40) NOT NULL Unique,
	UserPassword VARCHAR(20) NOT NULL
)

Create Table Users.Friends
(
	Userid1 INT NOT NULL,
	Userid2 INT NOT NULL,
	PRIMARY KEY(Userid1,userid2),
	Foreign Key(Userid1) references Users.User_Info(Userid),
	Foreign Key(Userid2) references Users.User_Info(Userid)
)

Create Table Users.Chatgroup
(
	Groupid INT NOT NULL identity(1,1) Primary Key,
	Groupname VARCHAR(50),
	GroupOwner INT NOT NULL Foreign Key References Users.User_Info(Userid) 
)
Create Table Users.ChatgroupMem
(
	Memid INT NOT NULL ,
	Groupid INT NOT NULL,
	Primary Key (Memid,Groupid),
	Foreign Key (Memid) References Users.User_Info(Userid),
	Foreign Key (Groupid) References Users.Chatgroup(Groupid)
)
Create Table Users.Online 
(
	Userid INT NOT NULL PRIMARY KEY,
	IP_addrr VARCHAR(20),
	FOREIGN KEY (Userid) References Users.User_Info(Userid) 
)

Create Table Users.Messages
(
	Messageid INT NOT NULL Identity(1,1) PRIMARY KEY,
	From_uid INT NOT NULL,
	To_gid INT NOT NULL,
	Body VARCHAR(1000) NOT NULL,
	Date_commit DATETIME NOT NULL,
	-- 删除From_uid外码约束的原因：当一个用户uid注销时，必须先删除这里的消息才能删除，
	-- 这样会导致别人也看不见uid之前发的消息
	-- Foreign Key (From_uid) References Users.User_Info(Userid),
	Foreign Key (To_gid) References Users.Chatgroup(Groupid)
)
---------------------------------------------------------------------
-- insert database's administrators
---------------------------------------------------------------------
Set IDENTITY_INSERT Administrator.Mem_Info ON
Insert Administrator.Mem_Info(Memid, Memname, MemPassword)
	values(0,'lrx','123456');
Insert Administrator.Mem_Info(Memid, Memname, MemPassword)
	values(1,'wy','123456');
Insert Administrator.Mem_Info(Memid, Memname, MemPassword)
	values(2,'qwh','123456');
Insert Administrator.Mem_Info(Memid, Memname, MemPassword)
	values(3,'ly','123456');
Set IDENTITY_INSERT Administrator.Mem_Info OFF

Set IDENTITY_INSERT Users.User_Info ON
Insert Users.User_Info(Userid,Username,UserPassword)
	values(0,'lrx','123456');
Insert Users.User_Info(Userid,Username,UserPassword)
	values(1,'wy','123456');
Insert Users.User_Info(Userid,Username,UserPassword)
	values(2,'qwh','123456');
Insert Users.User_Info(Userid,Username,UserPassword)
	values(3,N'ly','123456');
Set IDENTITY_INSERT Users.User_Info OFF

Set IDENTITY_INSERT Users.Chatgroup ON
Insert Users.Chatgroup(Groupid,Groupname,Groupowner)
	values(0,'group1',0);
Set IDENTITY_INSERT Users.Chatgroup OFF
