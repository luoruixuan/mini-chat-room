--
-- 由SQLiteStudio v3.1.1 产生的文件 周六 6月 9 19:40:18 2018
--
-- 文本编码：UTF-8
--
PRAGMA foreign_keys = off;
BEGIN TRANSACTION;

-- 表：Administrator_Mem_Info
DROP TABLE IF EXISTS Administrator_Mem_Info;

CREATE TABLE Administrator_Mem_Info (
    Memid       INTEGER      NOT NULL
                             PRIMARY KEY AUTOINCREMENT,
    Memname     VARCHAR (40) NOT NULL
                             UNIQUE,
    MemPassword VARCHAR (20) NOT NULL
);

INSERT INTO Administrator_Mem_Info (
                                       Memid,
                                       Memname,
                                       MemPassword
                                   )
                                   VALUES (
                                       0,
                                       'lrx',
                                       '123456'
                                   );

INSERT INTO Administrator_Mem_Info (
                                       Memid,
                                       Memname,
                                       MemPassword
                                   )
                                   VALUES (
                                       1,
                                       'wy',
                                       '123456'
                                   );

INSERT INTO Administrator_Mem_Info (
                                       Memid,
                                       Memname,
                                       MemPassword
                                   )
                                   VALUES (
                                       2,
                                       'qwt',
                                       '123456'
                                   );

INSERT INTO Administrator_Mem_Info (
                                       Memid,
                                       Memname,
                                       MemPassword
                                   )
                                   VALUES (
                                       3,
                                       'ly',
                                       '123456'
                                   );


-- 表：Users_Chatgroup
DROP TABLE IF EXISTS Users_Chatgroup;

CREATE TABLE Users_Chatgroup (
    Groupid    INTEGER      NOT NULL
                            PRIMARY KEY AUTOINCREMENT,
    Groupname  VARCHAR (50),
    GroupOwner INTEGER      NOT NULL,
    FOREIGN KEY (
        GroupOwner
    )
    REFERENCES Users_User_Info (Userid) 
);

INSERT INTO Users_Chatgroup (
                                Groupid,
                                Groupname,
                                GroupOwner
                            )
                            VALUES (
                                0,
                                'group1',
                                0
                            );

INSERT INTO Users_Chatgroup (
                                Groupid,
                                Groupname,
                                GroupOwner
                            )
                            VALUES (
                                1,
                                't',
                                1
                            );


-- 表：Users_ChatgroupMem
DROP TABLE IF EXISTS Users_ChatgroupMem;

CREATE TABLE Users_ChatgroupMem (
    Memid   INTEGER NOT NULL,
    Groupid INTEGER NOT NULL,
    PRIMARY KEY (
        Memid,
        Groupid
    ),
    FOREIGN KEY (
        Memid
    )
    REFERENCES Users_User_Info (Userid),
    FOREIGN KEY (
        Groupid
    )
    REFERENCES Users_Chatgroup (Groupid) 
);

INSERT INTO Users_ChatgroupMem (
                                   Memid,
                                   Groupid
                               )
                               VALUES (
                                   1,
                                   1
                               );

INSERT INTO Users_ChatgroupMem (
                                   Memid,
                                   Groupid
                               )
                               VALUES (
                                   0,
                                   0
                               );

INSERT INTO Users_ChatgroupMem (
                                   Memid,
                                   Groupid
                               )
                               VALUES (
                                   1,
                                   0
                               );


-- 表：Users_Friends
DROP TABLE IF EXISTS Users_Friends;

CREATE TABLE Users_Friends (
    Userid1 INTEGER NOT NULL,
    Userid2 INTEGER NOT NULL,
    PRIMARY KEY (
        Userid1,
        userid2
    ),
    FOREIGN KEY (
        Userid1
    )
    REFERENCES Users_User_Info (Userid),
    FOREIGN KEY (
        Userid2
    )
    REFERENCES Users_User_Info (Userid) 
);


-- 表：Users_Messages
DROP TABLE IF EXISTS Users_Messages;

CREATE TABLE Users_Messages (
    Messageid   INTEGER        NOT NULL
                               PRIMARY KEY AUTOINCREMENT,
    From_uid    INTEGER        NOT NULL,
    To_gid      INTEGER        NOT NULL,
    Body        VARCHAR (1000) NOT NULL,
    Date_commit DATETIME       NOT NULL,-- 删除From_uid外码约束的原因：当一个用户uid注销时，必须先删除这里的消息才能删除，
    /* 这样会导致别人也看不见uid之前发的消息 */FOREIGN KEY (
        To_gid
    )
    REFERENCES Users_Chatgroup (Groupid) 
);


-- 表：Users_Online
DROP TABLE IF EXISTS Users_Online;

CREATE TABLE Users_Online (
    Userid   INTEGER      NOT NULL
                          PRIMARY KEY,
    IP_addrr VARCHAR (20),
    FOREIGN KEY (
        Userid
    )
    REFERENCES Users_User_Info (Userid) 
);


-- 表：Users_User_Info
DROP TABLE IF EXISTS Users_User_Info;

CREATE TABLE Users_User_Info (
    Userid       INTEGER      NOT NULL
                              PRIMARY KEY AUTOINCREMENT,
    Username     VARCHAR (40) NOT NULL
                              UNIQUE,
    UserPassword VARCHAR (20) NOT NULL
);

INSERT INTO Users_User_Info (
                                Userid,
                                Username,
                                UserPassword
                            )
                            VALUES (
                                0,
                                'lrx',
                                '123456'
                            );

INSERT INTO Users_User_Info (
                                Userid,
                                Username,
                                UserPassword
                            )
                            VALUES (
                                1,
                                'wy',
                                '123456'
                            );

INSERT INTO Users_User_Info (
                                Userid,
                                Username,
                                UserPassword
                            )
                            VALUES (
                                2,
                                'qwt',
                                '123456'
                            );

INSERT INTO Users_User_Info (
                                Userid,
                                Username,
                                UserPassword
                            )
                            VALUES (
                                3,
                                'ly',
                                '123456'
                            );


COMMIT TRANSACTION;
PRAGMA foreign_keys = on;
