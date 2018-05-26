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
	Memid INT NOT NULL Primary Key,
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
	Userid INT NOT NULL Primary Key,
	Username VARCHAR(40) NOT NULL Unique,
	UserPassword VARCHAR(20) NOT NULL
)

Create Table Users.Friends
(
	Userid1 INT NOT NULL,
	Userid2 INT NOT NULL,
	PRIMARY KEY(Userid1,userid2)
)

Create Table Users.Chatgroup
(
	Groupid INT NOT NULL Primary Key,
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
	Messageid INT NOT NULL PRIMARY KEY,
	From_uid INT NOT NULL,
	To_uid INT NOT NULL,
	Body VARCHAR(1000) NOT NULL,
	Date_commit DATETIME NOT NULL,
	Foreign Key (From_uid) References Users.User_Info(Userid),
	Foreign Key (To_uid) References Users.User_Info(Userid)
)
---------------------------------------------------------------------
-- insert database's administrators
---------------------------------------------------------------------
Insert Administrator.Mem_Info(Memid, Memname, MemPassword)
	values(0,'lrx','123456');
Insert Administrator.Mem_Info(Memid, Memname, MemPassword)
	values(1,'wy','123456');
Insert Administrator.Mem_Info(Memid, Memname, MemPassword)
	values(2,'qwh','123456');
Insert Administrator.Mem_Info(Memid, Memname, MemPassword)
	values(3,'ly','123456');

Insert Users.User_Info(Userid,Username,UserPassword)
	values(0,'lrx','123456');
Insert Users.User_Info(Userid,Username,UserPassword)
	values(1,'wy','123456');
Insert Users.User_Info(Userid,Username,UserPassword)
	values(2,'qwh','123456');
Insert Users.User_Info(Userid,Username,UserPassword)
	values(3,N'ly','123456');
	
Insert Users.Chatgroup(Groupid,Groupname,Groupowner)
	values(0,'group1',0);
