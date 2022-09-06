import os.path
import threading
import socket
import sqlite3
import shutil
import ast
from typing import Tuple
import numpy
import datetime


BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MYFORMAT = 'utf-8'


# host = '192.168.100.6'
host = '127.0.0.1'

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((host, 59000))
server.listen()


clients = [] # все клиенты онлайн
nicknames = [] # массив из user_name
usersid = [] # массив из user_id





def getRequest(client, nick, id):
    global clients, nicknames, userid
    db_path = os.path.join(BASE_DIR, 'ChatDataBase.db')
    base = sqlite3.connect(db_path)
    cur = base.cursor()
    request = ''
    while request != 'exit':
        try:
            request = client.recv(4).decode(MYFORMAT)
            if request == 'send':
                check = False
                ConversationNumber = numpy.frombuffer(client.recv(8), dtype=numpy.int64)
                CurConversation = cur.execute('select * from conversation where conversation_id = ?', (ConversationNumber.item(),)).fetchall()
                base.commit()
                if len(CurConversation) == 1:
                    Data = cur.execute('select * from conversation_member where conversation_id = ? and user_id = ?', (ConversationNumber.item(), id)).fetchall()
                    base.commit()
                    if len(Data) == 1:
                        check = True
                if not check:
                    print('suspicious request')
                else:
                    MessageType = numpy.frombuffer(client.recv(8), dtype=numpy.int64)
                    MessageType = MessageType.item()
                    if MessageType == 1:
                        sz = numpy.frombuffer(client.recv(8), dtype=numpy.int64)
                        Message = client.recv(sz.item()).decode(MYFORMAT)
                        CurDateTime = str(datetime.datetime.utcnow())
                        MsgSz = int(cur.execute('select count(*) from message').fetchone()[0]) + 1
                        base.commit()
                        DataMsg = (MsgSz, nick, 1, Message, CurDateTime, ConversationNumber.item(), 0, '')
                        cur.execute('insert into message values(?, ?, ?, ?, ?, ?, ?, ?)', DataMsg)
                        base.commit()
                        # cur.execute('update conversation set last_message = ? where conversation_id = ?', (str(MsgSz), ConversationNumber.item()))
                        # base.commit()
                        SendMessageThread = threading.Thread(target=sendMessage, args=(CurConversation, DataMsg))
                        SendMessageThread.start()
                        # DataMsg = str(DataMsg).encode(MYFORMAT)
                        # NumpyInt = numpy.int64(len(DataMsg))
                        # client.send(NumpyInt.tobytes())
                        # client.send(DataMsg)
                    if MessageType == 2:
                        FileName = getFile(client, nick)
                        CurDateTime = str(datetime.datetime.utcnow())
                        MsgSz = int(cur.execute('select count(*) from message').fetchone()[0]) + 1
                        DataMsg = (MsgSz, nick, 2, '', CurDateTime, ConversationNumber.item(), 0, FileName)
                        cur.execute('insert into message values(?, ?, ?, ?, ?, ?, ?, ?)', DataMsg)
                        base.commit()
                        # cur.execute('update conversation set last_message = ? where conversation_id = ?', (str(MsgSz), ConversationNumber.item()))
                        # base.commit()
                        SendMessageThread = threading.Thread(target=sendMessage, args=(CurConversation, DataMsg))
                        SendMessageThread.start()
                        # DataMsg = str(DataMsg).encode(MYFORMAT)
                        # NumpyInt = numpy.int64(len(DataMsg))
                        # client.send(NumpyInt.tobytes())
                        # client.send(DataMsg)
                    if MessageType == 3:
                        sz = numpy.frombuffer(client.recv(8), dtype=numpy.int64)
                        Message = client.recv(sz.item()).decode(MYFORMAT)  
                        FileName = getFile(client, nick)
                        CurDateTime = str(datetime.datetime.utcnow())
                        MsgSz = int(cur.execute('select count(*) from message').fetchone()[0]) + 1
                        DataMsg = (MsgSz, nick, 3, Message, CurDateTime, ConversationNumber.item(), 0, FileName)
                        cur.execute('insert into message values(?, ?, ?, ?, ?, ?, ?, ?)', DataMsg)
                        base.commit()
                        # cur.execute('update conversation set last_message = ? where conversation_id = ?', (str(MsgSz), ConversationNumber.item()))
                        # base.commit()
                        SendMessageThread = threading.Thread(target=sendMessage, args=(CurConversation, DataMsg))
                        SendMessageThread.start()

                        # DataMsg = str(DataMsg).encode(MYFORMAT)
                        # NumpyInt = numpy.int64(len(DataMsg))
                        # client.send(NumpyInt.tobytes())
                        # client.send(DataMsg)
            if request == 'conv':
                sz = numpy.frombuffer(client.recv(8), dtype=numpy.int64)
                ConvName = str(client.recv(sz.item()).decode(MYFORMAT))
                ConvPhoto = 'None'.encode(MYFORMAT)
                print('NAMEEEE' + ConvName)
                if ConvName != 'default':
                    MyPath = os.path.join(BASE_DIR, 'MainFolder' + '\\' + 'DefaultConv.jpg')
                    NumpyInt = numpy.int64(os.path.getsize(MyPath))
                    file = open(MyPath, "rb")
                    PhotoBytes = file.read(NumpyInt.item())
                    file.close()
                    ConvPhoto = str(('DefaultConv.jpg', PhotoBytes)).encode(MYFORMAT)
                sz = numpy.frombuffer(client.recv(8), dtype=numpy.int64)
                ConvUsers = client.recv(sz.item()).decode(MYFORMAT)
                print(ConvUsers)
                CurDateTime = str(datetime.datetime.utcnow())
                MsgSz = int(cur.execute('select count(*) from conversation').fetchone()[0]) + 1
                base.commit()
                if ConvName != 'default':
                    DataMsg = (MsgSz, ConvName, 'DefaultConv.jpg', '')
                else:
                    DataMsg = (MsgSz, ConvName, '', '')
                cur.execute('insert into conversation values(?, ?, ?, ?)', DataMsg)
                base.commit()
                
                if ConvName != 'default':
                    os.mkdir('Conversations' + '\\' + str(MsgSz))
                    original = os.path.join(BASE_DIR, 'MainFolder\\DefaultConv.jpg')
                    target = os.path.join(BASE_DIR, 'Conversations' + '\\' + str(MsgSz) + '\\DefaultConv.jpg')
                    shutil.copyfile(original, target)

                ConvUsers = ast.literal_eval(ConvUsers)
                AllConvUsersWithData = [] # (2, 'default.jpg', 'Me')
                ConversationData = ()  # user_id, joined_datetime, left_datetime, lms_checked
                ActualConvUsers = []
                UsersPhoto = dict()
                print(ConvUsers)
                for item in ConvUsers:
                    check = cur.execute('select user_id, profile_photo, user_name from user where user_id = ?', (item,)).fetchall()
                    base.commit()
                    print(str(item) + '-----------------' + str(check))
                    if len(check)==1:
                        MyPath = os.path.join(BASE_DIR, 'Users' + '\\' + check[0][2] + '\\' + check[0][1])
                        NumpyInt = numpy.int64(os.path.getsize(MyPath))
                        file = open(MyPath, "rb")
                        PhotoBytes = file.read(NumpyInt.item())
                        file.close()
                        UsersPhoto[check[0]] = (check[0][1], PhotoBytes)
                        ActualConvUsers.append(item)
                        AllConvUsersWithData.append(check[0])
                        if item == id:
                            ConversationData = (item, CurDateTime, '', 0)
                        cur.execute('insert into conversation_member values(?, ?, ?, ?, ?)', (item, MsgSz, CurDateTime, '', 0))
                        base.commit()
                DataMsg = str(DataMsg).encode(MYFORMAT)
                AllConvUsersWithData = str(AllConvUsersWithData).encode(MYFORMAT)
                ConversationData = str(ConversationData).encode(MYFORMAT)
                UsersPhoto = str(UsersPhoto).encode(MYFORMAT)
                sendConversation(ActualConvUsers, DataMsg, AllConvUsersWithData, ConversationData, ConvPhoto, UsersPhoto)
        except:
            request = 'exit'
            i = usersid.index(id)
            clients.remove(clients[i])
            usersid.remove(usersid[i])
            nicknames.remove(nicknames[i])

            

            



def sendConversation(ConvUsers, ConvData, AllConvUsersWithData, ConversationData, ConvPhoto, UsersPhoto):
    for item in ConvUsers:
        try:
            i = usersid.index(item)
            NumpyInt = numpy.int64(len(ConvData))
            clients[i].send('conv'.encode(MYFORMAT))
            clients[i].send(NumpyInt.tobytes())
            clients[i].send(ConvData)
            NumpyInt = numpy.int64(len(AllConvUsersWithData))
            clients[i].send(NumpyInt.tobytes())
            clients[i].send(AllConvUsersWithData)
            NumpyInt = numpy.int64(len(ConversationData))
            clients[i].send(NumpyInt.tobytes())
            clients[i].send(ConversationData)
            NumpyInt = numpy.int64(len(ConvPhoto))
            clients[i].send(NumpyInt.tobytes())
            clients[i].send(ConvPhoto)
            NumpyInt = numpy.int64(len(UsersPhoto))
            clients[i].send(NumpyInt.tobytes())
            clients[i].send(UsersPhoto)
        except:
            print("FK")




                    

def sendMessage(CurConversation, Msg):
    global clients, nicknames, userid
    db_path = os.path.join(BASE_DIR, 'ChatDataBase.db')
    base = sqlite3.connect(db_path)
    cur = base.cursor()
    AllUsersFromConv = cur.execute('select * from conversation_member where conversation_id = ?',(CurConversation[0][0],)).fetchall()
    base.commit()
    for item in AllUsersFromConv:
        try:
            i = usersid.index(item[0])
            MsgToSend = (CurConversation[0], Msg)
            MsgToSend = str(MsgToSend).encode(MYFORMAT)
            NumpyInt = numpy.int64(len(MsgToSend))
            clients[i].send('nmes'.encode(MYFORMAT))
            clients[i].send(NumpyInt.tobytes())
            clients[i].send(MsgToSend)
        except:
            print("FK")


def getFile(client, nick):
    sz = numpy.frombuffer(client.recv(8), dtype=numpy.int64)
    filename = client.recv(sz.item()).decode(MYFORMAT)
    filesize = numpy.frombuffer(client.recv(8), dtype=numpy.int64)
    MyPath = os.path.join(BASE_DIR, "Users"+"\\"+str(nick)+"\\"+str(filename))
    counter = 0
    name, extension = filename.split('.')
    TempName = filename
    while(os.path.exists(MyPath)):
        counter+=1
        TempName = name + f' ({counter}).' + extension
        MyPath = os.path.join(BASE_DIR, "Users"+"\\"+str(nick)+"\\"+str(TempName))
    file = open(MyPath, 'wb+')
    file.write(client.recv(filesize.item()))
    file.seek(0, os.SEEK_END)
    while file.tell() < filesize:
        file.write(client.recv(filesize.item() - file.tell()))
        file.seek(0, os.SEEK_END)
    file.close()
    return TempName



def sendFile(client, fpath, file):
    NumpyInt = numpy.int64(len(file.encode(MYFORMAT)))
    client.send(NumpyInt.tobytes())
    client.send(file.encode(MYFORMAT))
    NumpyInt = numpy.int64(os.path.getsize(fpath))
    client.send(NumpyInt.tobytes())
    file = open(fpath, "rb")
    client.send(file.read(NumpyInt.item()))
    file.close()

def sendNewUserData(data):
    global clients, nicknames, userid
    for i in range(len(usersid)):
        if usersid[i] != int(data[0]):
            NumpyInt = numpy.int64(len(data))
            clients[i].send('user'.encode(MYFORMAT))
            clients[i].send(NumpyInt.tobytes())
            clients[i].send(data)

def initialize_client(client, address):
    global usersid, clients, nicknames
    db_path = os.path.join(BASE_DIR, 'ChatDataBase.db')
    base = sqlite3.connect(db_path)
    cur = base.cursor()
    try:
        while True:
            global clients, nicknames, userid
            ans = client.recv(3).decode(MYFORMAT)
            if ans == '':
                break
            print(f"client sent {ans}")
            if ans == "reg":
                print("reg")
                sz = numpy.frombuffer(client.recv(8), dtype=numpy.int64)
                nick = client.recv(sz.item()).decode(MYFORMAT)
                sz = numpy.frombuffer(client.recv(8), dtype=numpy.int64)
                password = client.recv(sz.item()).decode(MYFORMAT)
                profile_photo = "default.jpg"
                check = cur.execute('select * from user where user_name = ?', (nick,)).fetchall()
                base.commit()
                print(len(check))
                if len(check) == 0 and str(nick) != "MainFolder":
                    allUsers = cur.execute('select count(*) from user').fetchone()[0]
                    base.commit()
                    cur.execute('insert into user values(?, ?, ?, ?)', (allUsers+1, profile_photo, nick, password))
                    base.commit()
                    client.send("success".encode(MYFORMAT))
                    NumpyInt = numpy.int64(allUsers+1)
                    client.send(NumpyInt.tobytes())
                    clients.append(client)
                    nicknames.append(str(nick))
                    usersid.append(allUsers+1)
                    print(clients)
                    print(nicknames)
                    print(usersid)
                    os.mkdir('Users' + '\\' + str(nick))
                    original = os.path.join(BASE_DIR, 'MainFolder\\default.jpg')
                    target = os.path.join(BASE_DIR, 'Users' + '\\' + str(nick) + '\\default.jpg')
                    shutil.copyfile(original, target)
                    sendFile(client, original, 'default.jpg')
                    UserMap = cur.execute('select user_id, profile_photo, user_name from user where user_id != ?',(allUsers+1,)).fetchall()
                    base.commit()
                    UserMapString = str(UserMap).encode(MYFORMAT)
                    NumpyInt = numpy.int64(len(UserMapString))
                    client.send(NumpyInt.tobytes())
                    client.send(UserMapString)
                    base.close()
                    data = str((allUsers+1, profile_photo, nick)).encode(MYFORMAT)
                    sendNewUserData(data)
                    GetRequestThread = threading.Thread(target=getRequest, args=(client, nick, allUsers+1))
                    GetRequestThread.start()
                    break
                else:
                    client.send('failure'.encode(MYFORMAT))
            if ans == "log":
                print("log")
                sz = numpy.frombuffer(client.recv(8), dtype=numpy.int64)
                nick = client.recv(sz.item()).decode(MYFORMAT)
                sz = numpy.frombuffer(client.recv(8), dtype=numpy.int64)
                password = client.recv(sz.item()).decode(MYFORMAT)
                check = cur.execute('select * from user where user_name = ? and password = ?', (nick, password)).fetchall()
                base.commit()
                print(len(check))
                if len(check) == 1:
                    client.send("success".encode(MYFORMAT))
                    NumpyInt = numpy.int64(int(check[0][0]))
                    client.send(NumpyInt.tobytes())
                    if int(check[0][0]) not in usersid:
                        clients.append(client)
                        nicknames.append(str(nick))
                        usersid.append(int(check[0][0]))
                    else:
                        i = usersid.index(check[0][0])
                        clients[i].close()
                        clients[i] = client
                    print(clients)
                    print(nicknames)
                    print(usersid)
                    # Передача данных
                    UserConversations = cur.execute('select * from conversation_member where user_id = ?', (int(check[0][0]),)).fetchall() # Все conversation_member текущего юзера
                    base.commit()
                    UserMap = cur.execute('select user_id, profile_photo, user_name from user where user_id != ?',(int(check[0][0]),)).fetchall()
                    base.commit()
                    AllConversations = dict()
                    AllConversationsUsers = dict()
                    ConversationPhoto = dict()
                    UsersPhoto = dict()
                    for item in UserConversations:
                        CurConversation = cur.execute('select * from conversation where conversation_id = ?', (item[1],)).fetchall() # Текущая беседа
                        base.commit()
                        AllConversationMessages = cur.execute('select * from message where conversation_id = ? order by message_id desc', (item[1],)).fetchall() # Все сообщения беседы
                        base.commit()
                        AllConversations[CurConversation[0]] = AllConversationMessages # Беседа и все ее сообщения --- нужно отправить
                        AllCurConversationMembers = cur.execute('select * from conversation_member where conversation_id = ?', (item[1],)).fetchall() # Все conversation_member беседы
                        base.commit()
                        AllCurConversationUsers = set()
                        for it in AllCurConversationMembers:
                            CurUser = cur.execute('select user_id, profile_photo, user_name from user where user_id = ?', (it[0],)).fetchall()[0]
                            base.commit()
                            AllCurConversationUsers.add(CurUser)
                            Path = os.path.join(BASE_DIR, 'Users' + '\\' + str(CurUser[2])+ '\\' +str(CurUser[1]))
                            NumpyInt = numpy.int64(os.path.getsize(Path))
                            Photo = open(Path, "rb")
                            PhotoBytes = Photo.read(NumpyInt.item())
                            Photo.close()
                            UsersPhoto[CurUser] = (str(CurUser[1]), PhotoBytes)
                        AllConversationsUsers[CurConversation[0]] = AllCurConversationUsers # Беседа и user данные ее участников --- нужно отправить
                        if str(CurConversation[0][1]) == 'default':
                            ConversationPhoto[CurConversation[0]] = None
                        else:
                            Path = os.path.join(BASE_DIR, "Conversations\\"+str(CurConversation[0][0])+"\\"+str(CurConversation[0][2]))
                            NumpyInt = numpy.int64(os.path.getsize(Path))
                            Photo = open(Path, "rb")
                            PhotoBytes = Photo.read(NumpyInt.item())
                            Photo.close()
                            ConversationPhoto[CurConversation[0]] = (str(CurConversation[0][2]), PhotoBytes)
                    UserMapString = str(UserMap).encode(MYFORMAT)
                    AllConversationsString = str(AllConversations).encode(MYFORMAT)
                    AllConversationsUsersString = str(AllConversationsUsers).encode(MYFORMAT)
                    ConversationPhotoString = str(ConversationPhoto).encode(MYFORMAT)
                    UsersPhotoString = str(UsersPhoto).encode(MYFORMAT)
                    NumpyInt = numpy.int64(len(UserMapString))
                    client.send(NumpyInt.tobytes())
                    client.send(UserMapString)

                    NumpyInt = numpy.int64(len(AllConversationsString))
                    client.send(NumpyInt.tobytes())
                    client.send(AllConversationsString)

                    NumpyInt = numpy.int64(len(AllConversationsUsersString))
                    client.send(NumpyInt.tobytes())
                    client.send(AllConversationsUsersString)

                    NumpyInt = numpy.int64(len(ConversationPhotoString))
                    client.send(NumpyInt.tobytes())
                    client.send(ConversationPhotoString)

                    NumpyInt = numpy.int64(len(UsersPhotoString))
                    client.send(NumpyInt.tobytes())
                    client.send(UsersPhotoString)

                    base.close()
                    GetRequestThread = threading.Thread(target=getRequest, args=(client, nick, int(check[0][0])))
                    GetRequestThread.start()
                    break
                else:
                    client.send('failure'.encode(MYFORMAT))
    except:
        print("FK")


def receive():
    print('Server is running and listening ...')
    while True:
        client, address = server.accept()
        print(f'connection is established with {str(address)}')
        thread = threading.Thread(target=initialize_client, args=(client, address))
        thread.start()

receive()