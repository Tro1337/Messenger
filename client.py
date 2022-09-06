import threading
import socket
import sys
import numpy
import shutil
import ast
import os
import time

import PySimpleGUI as sg

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MYFORMAT = 'utf-8'

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# client.connect(('192.168.100.6', 59000))
# client.connect(('178.184.13.94', 59000))
client.connect(('127.0.0.1', 59000))

MyPath = os.path.join(BASE_DIR, "Users")
if os.path.exists(MyPath):
    shutil.rmtree(MyPath)
MyPath = os.path.join(BASE_DIR, "Conversations")
if os.path.exists(MyPath):
    shutil.rmtree(MyPath)
UserMap = []
AllConversations = dict()
AllConversationsUsers = dict()
AllConversations_Check = []
MyId = 0
NewConvAllConversations = dict()
NewConvAllConversationsUsers = dict()
FlagConv = True

def sendRequest(client, nick, id):
    global AllConversations, AllConversationsUsers, UserMap
    while True:
        print('Type of request?')
        request = input()
        client.send(request.encode(MYFORMAT))
        if request == 'send':
            print('Conversation number?')
            ConversationNumber = int(input())
            NumpyInt = numpy.int64(ConversationNumber)
            client.send(NumpyInt.tobytes())
            CurConversation = ""
            # ПОИСК КОНКРЕТНОЙ БЕСЕДЫ В ИНТЕРФЕЙСЕ ДОЛЖЕН ОТСУТСТВОВАТЬ
            for key in AllConversations:
                if int(key[0]) == ConversationNumber:
                    CurConversation = key
                    break
            print('TypeOfSend?')
            TypeOfSend = int(input())
            Type = numpy.int64(TypeOfSend)
            if TypeOfSend == 1:
                print('Enter message')
                TextToSend = input().encode(MYFORMAT)
                NumpyInt = numpy.int64(len(TextToSend))
                client.send(Type.tobytes())
                client.send(NumpyInt.tobytes())
                client.send(TextToSend)
            if TypeOfSend == 2:
                print('Enter path to file')
                MyPath = input()
                if os.path.isfile(MyPath):
                    client.send(Type.tobytes())
                    FileName = os.path.basename(MyPath)
                    sendFile(client, MyPath, FileName)
                else:
                    print('Something is wrong and you know it')
            if TypeOfSend == 3:
                print('Enter message')
                TextToSend = input().encode(MYFORMAT)
                NumpyInt = numpy.int64(len(TextToSend))
                print('Enter path to file')
                MyPath = input()
                if os.path.isfile(MyPath):
                    client.send(Type.tobytes())
                    client.send(NumpyInt.tobytes())
                    client.send(TextToSend)
                    FileName = os.path.basename(MyPath)
                    sendFile(client, MyPath, FileName)
                else:
                    print('Something is wrong and you know it')
            print("Беседа и все ее сообщения")
            print(AllConversations, sep="\n")
            print("Беседа и user данные ее участников", sep="\n")
            print(AllConversationsUsers)
        if request == 'conv':
            print("Введите название беседы")
            ConvName = input().encode(MYFORMAT)
            print("Введите участников беседы")
            ConvUsers = str(list(map(int, input().split(' ')))).encode(MYFORMAT)
            NumpyInt = numpy.int64(len(ConvName))
            client.send(NumpyInt.tobytes())
            client.send(ConvName)
            NumpyInt = numpy.int64(len(ConvUsers))
            client.send(NumpyInt.tobytes())
            client.send(ConvUsers)
            print(ConvUsers)



def getMessageInWindow(client):
    global AllConversations, AllConversationsUsers, UserMap, MYFORMAT
    while True:
        MsgType = client.recv(4).decode(MYFORMAT)
        # print(MsgType)
        if MsgType == 'nmes':
            sz = numpy.frombuffer(client.recv(8), dtype=numpy.int64)
            msg = client.recv(sz.item()).decode(MYFORMAT)
            pair = ast.literal_eval(msg)
            if len(AllConversations[pair[0]]) == 0:
                AllConversations[pair[0]].append(pair[1])
            else:
                AllConversations[pair[0]].insert(0, pair[1])

            if 'SaveData' in window.AllKeysDict:

                for i, j in AllConversations.items():
                    nick = ""
                    if i[1] == "default":
                        for n in AllConversationsUsers[i]:
                            if n[0] != MyId:
                                nick = n[2]
                                break

                        # save_keys.append(str(i))
                        create_key = []
                        for k in range(3):
                            create_key.append(str(str(i) + str(k)))

                        window[create_key[0]].update(j[0][1])
                        window[create_key[1]].update(j[0][3])
                        window[create_key[2]].update(str(((j[0][4].split(".")[0].split(
                            ' '))[::-1])[0]) + "\n" + str(
                            ((j[0][
                                  4].split(
                                ".")[0].split(' '))[::-1])[
                                1]))
            else:
                AllConversations_Check = []
                for i in AllConversations[pair[0]]:
                    AllConversations_Check.append(i)

                arr = []
                for i in reversed(AllConversations_Check):
                    arr.append(str(i[1]) + "  :  " + str(i[3]) + "        " + str(
                        ((i[4].split(".")[0].split(' '))[::-1])[0]) + " " + str(
                        ((i[4].split(".")[0].split(' '))[::-1])[1]))

                window['chat'].update(arr)
                window['chat'].Widget.yview_moveto(1.0)

        if MsgType == 'conv':

            sz = numpy.frombuffer(client.recv(8), dtype=numpy.int64)
            ConvData = ast.literal_eval(client.recv(sz.item()).decode(MYFORMAT))
            sz = numpy.frombuffer(client.recv(8), dtype=numpy.int64)
            AllConvUsersWithData = ast.literal_eval(client.recv(sz.item()).decode(MYFORMAT))
            sz = numpy.frombuffer(client.recv(8), dtype=numpy.int64)
            ConversationData = ast.literal_eval(client.recv(sz.item()).decode(MYFORMAT))
            sz = numpy.frombuffer(client.recv(8), dtype=numpy.int64)
            ConvPhoto = ast.literal_eval(client.recv(sz.item()).decode(MYFORMAT))
            sz = numpy.frombuffer(client.recv(8), dtype=numpy.int64)
            UsersPhoto = ast.literal_eval(client.recv(sz.item()).decode(MYFORMAT))

            if ConvData[1] != 'default':
                os.mkdir('Conversations' + '\\' + str(ConvData[0]))
                MyPath = os.path.join(BASE_DIR, 'Conversations' + '\\' + str(ConvData[0]) + '\\' + str(ConvData[2]))
                file = open(MyPath, 'wb+')
                file.write(ConvPhoto[1])
                file.close()

            for key, value in UsersPhoto.items():
                MyPath = os.path.join(BASE_DIR, 'Users' + '\\' + str(key[2]))
                if not os.path.exists(MyPath):
                    os.mkdir(MyPath)
                MyPath = os.path.join(BASE_DIR, 'Users' + '\\' + str(key[2]) + '\\' + str(key[1]))
                file = open(MyPath, 'wb+')
                file.write(value[1])
                file.close()

            AllConversationsUsers[ConvData] = AllConvUsersWithData
            AllConversations[ConvData] = []
            NewConvAllConversations = AllConversations
            NewConvAllConversationsUsers = AllConversationsUsers

        if MsgType == 'user':
            sz = numpy.frombuffer(client.recv(8), dtype=numpy.int64)
            Data = ast.literal_eval(client.recv(sz.item()).decode(MYFORMAT))
            UserMap.append(Data)


def sendFile(client, fpath, file):
    NumpyInt = numpy.int64(len(file.encode(MYFORMAT)))
    client.send(NumpyInt.tobytes())
    client.send(file.encode(MYFORMAT))
    NumpyInt = numpy.int64(os.path.getsize(fpath))
    client.send(NumpyInt.tobytes())
    file = open(fpath, "rb")
    client.send(file.read(NumpyInt.item()))
    file.close()


def getFile(client, nick):
    sz = numpy.frombuffer(client.recv(8), dtype=numpy.int64)
    filename = client.recv(sz.item()).decode(MYFORMAT)
    filesize = numpy.frombuffer(client.recv(8), dtype=numpy.int64)
    os.mkdir('Users')
    MyPath = os.path.join(BASE_DIR, "Users" + "\\" + str(nick))
    os.mkdir(MyPath)
    MyPath = os.path.join(BASE_DIR, "Users" + "\\" + str(nick) + "\\" + str(filename))
    file = open(MyPath, 'wb+')
    file.write(client.recv(filesize.item()))
    file.seek(0, os.SEEK_END)
    while file.tell() < filesize:
        file.write(client.recv(filesize.item() - file.tell()))
        file.seek(0, os.SEEK_END)
    file.close()


def application_start():
    global AllConversations, AllConversationsUsers, UserMap
    login = ''
    password = ''
    MyId = 0
    while True:
        inp = input('reg or log >>> ')
        client.send(inp.encode(MYFORMAT))
        if inp == 'reg':
            print('Enter login')
            login = input()
            NumpyInt = numpy.int64(len(login.encode(MYFORMAT)))
            client.send(NumpyInt.tobytes())
            client.send(login.encode(MYFORMAT))
            print('Enter_password')
            password = input()
            NumpyInt = numpy.int64(len(password.encode(MYFORMAT)))
            client.send(NumpyInt.tobytes())
            client.send(password.encode(MYFORMAT))
            check = client.recv(7).decode(MYFORMAT)
            if check == "success":
                sz = numpy.frombuffer(client.recv(8), dtype=numpy.int64)
                MyId = sz.item()
                print(f'My id is {MyId} and my nick is {login}')
                getFile(client, login)
                os.mkdir('Conversations')
                sz = numpy.frombuffer(client.recv(8), dtype=numpy.int64)
                UserMap = client.recv(sz.item())
                while len(UserMap) < sz:
                    UserMap += client.recv(sz.item() - len(UserMap))
                UserMap = ast.literal_eval(UserMap.decode(MYFORMAT))
                print(UserMap)
                SendRequestThread = threading.Thread(target=sendRequest, args=(client, login, MyId))
                SendRequestThread.start()
                GetMessageThread = threading.Thread(target=getMessage, args=(client,))
                GetMessageThread.start()
                break
            else:
                print('Such user is already exists')
        if inp == 'log':
            print('Enter login')
            login = input()
            NumpyInt = numpy.int64(len(login.encode(MYFORMAT)))
            client.send(NumpyInt.tobytes())
            client.send(login.encode(MYFORMAT))
            print('Enter_password')
            password = input()
            NumpyInt = numpy.int64(len(password.encode(MYFORMAT)))
            client.send(NumpyInt.tobytes())
            client.send(password.encode(MYFORMAT))
            check = client.recv(7).decode(MYFORMAT)
            print('check = ' + check)
            if check == 'success':
                NumpyInt = numpy.frombuffer(client.recv(8), dtype=numpy.int64)
                MyId = NumpyInt.item()
                print(f'My id is {MyId} and my nick is {login}')
                # getFile(client, login)

                ConversationPhoto = dict()
                UsersPhoto = dict()

                sz = numpy.frombuffer(client.recv(8), dtype=numpy.int64)
                UserMap = client.recv(sz.item())
                while len(UserMap) < sz:
                    UserMap += client.recv(sz.item() - len(UserMap))
                UserMap = ast.literal_eval(UserMap.decode(MYFORMAT))

                sz = numpy.frombuffer(client.recv(8), dtype=numpy.int64)
                AllConversations = client.recv(sz.item())
                while len(AllConversations) < sz:
                    AllConversations += client.recv(sz.item() - len(AllConversations))
                AllConversations = ast.literal_eval(AllConversations.decode(MYFORMAT))

                sz = numpy.frombuffer(client.recv(8), dtype=numpy.int64)
                AllConversationsUsers = client.recv(sz.item())
                while len(AllConversationsUsers) < sz:
                    AllConversationsUsers += client.recv(sz.item() - len(AllConversationsUsers))
                AllConversationsUsers = ast.literal_eval(AllConversationsUsers.decode(MYFORMAT))

                sz = numpy.frombuffer(client.recv(8), dtype=numpy.int64)
                ConversationPhoto = client.recv(sz.item())
                while len(ConversationPhoto) < sz:
                    ConversationPhoto += client.recv(sz.item() - len(ConversationPhoto))
                ConversationPhoto = ast.literal_eval(ConversationPhoto.decode(MYFORMAT))

                sz = numpy.frombuffer(client.recv(8), dtype=numpy.int64)
                UsersPhoto = client.recv(sz.item())
                while len(UsersPhoto) < sz:
                    UsersPhoto += client.recv(sz.item() - len(UsersPhoto))
                UsersPhoto = ast.literal_eval(UsersPhoto.decode(MYFORMAT))

                os.mkdir('Conversations')
                for conversations, data in ConversationPhoto.items():
                    if conversations[1] != 'default':
                        MyPath = os.path.join(BASE_DIR, 'Conversations' + '\\' + str(conversations[0]))
                        os.mkdir(MyPath)
                        MyPath = os.path.join(BASE_DIR,
                                              'Conversations' + '\\' + str(conversations[0]) + "\\" + str(data[0]))
                        file = open(MyPath, 'wb+')
                        file.write(data[1])
                        file.close

                os.mkdir('Users')
                for user, data in UsersPhoto.items():
                    MyPath = os.path.join(BASE_DIR, 'Users' + '\\' + str(user[2]))
                    os.mkdir(MyPath)
                    MyPath = os.path.join(BASE_DIR, 'Users' + '\\' + str(user[2]) + '\\' + str(data[0]))
                    file = open(MyPath, 'wb+')
                    file.write(data[1])
                    file.close

                print('UserMap')
                print(UserMap)
                print("Беседа и все ее сообщения")
                print(AllConversations)
                print("Беседа и user данные ее участников")
                print(AllConversationsUsers)
                SendRequestThread = threading.Thread(target=sendRequest, args=(client, login, MyId))
                SendRequestThread.start()
                GetMessageThread = threading.Thread(target=getMessage, args=(client,))
                GetMessageThread.start()

                # print("Словарь типа ---- conversation_id : (user_id, joined_datetime, left_datetime, lms_checked)")
                # print(UserMap)
                # print("Беседа и все ее сообщения")
                # print(AllConversations)
                # print("Беседа и user данные ее участников")
                # print(AllConversationsUsers)
                # print("UsersPhoto")
                # print(UsersPhoto)
                # print("ConversationPhoto")
                # print(ConversationPhoto)
                break
            else:
                print('Could not log in')

def popupBoi(*args, title=None, button_color=None, background_color=None, text_color=None,
             button_type=sg.POPUP_BUTTONS_OK, auto_close=False,
             auto_close_duration=None, custom_text=(None, None), non_blocking=False, icon=None, line_width=None,
             font=None, no_titlebar=False, grab_anywhere=False,
             keep_on_top=None, location=(None, None), relative_location=(None, None), any_key_closes=False, image=None,
             modal=True, margins=None, disable_close=False, element_justification='c'):
    if not args:
        args_to_print = ['']
    else:
        args_to_print = args
    if line_width != None:
        local_line_width = line_width
    else:
        local_line_width = sg.MESSAGE_BOX_LINE_WIDTH
    _title = title if title is not None else args_to_print[0]

    layout = [[]]
    max_line_total, total_lines = 0, 0
    if image is not None:
        if isinstance(image, str):
            layout += [[sg.Image(filename=image)]]
        else:
            layout += [[sg.Image(data=image)]]

    for message in args_to_print:
        # fancy code to check if string and convert if not is not need. Just always convert to string :-)
        # if not isinstance(message, str): message = str(message)
        message = str(message)
        if message.count('\n'):  # if there are line breaks, then wrap each segment separately
            # message_wrapped = message         # used to just do this, but now breaking into smaller pieces
            message_wrapped = ''
            msg_list = message.split('\n')  # break into segments that will each be wrapped
            message_wrapped = '\n'.join([sg.textwrap.fill(msg, local_line_width) for msg in msg_list])
        else:
            message_wrapped = sg.textwrap.fill(message, local_line_width)
        message_wrapped_lines = message_wrapped.count('\n') + 1
        longest_line_len = max([len(l) for l in message.split('\n')])
        width_used = min(longest_line_len, local_line_width)
        max_line_total = max(max_line_total, width_used)
        # height = _GetNumLinesNeeded(message, width_used)
        height = message_wrapped_lines
        layout += [[
            sg.Text(message_wrapped, auto_size_text=True, text_color=text_color, background_color=background_color)]]
        total_lines += height

    if non_blocking:
        PopupButton = sg.DummyButton  # important to use or else button will close other windows too!
    else:
        PopupButton = sg.Button
    # show either an OK or Yes/No depending on paramater
    if custom_text != (None, None):
        if type(custom_text) is not tuple:
            layout += [[PopupButton(custom_text, size=(len(custom_text), 1), button_color=button_color, focus=True,
                                    bind_return_key=True)]]
        elif custom_text[1] is None:
            layout += [[
                PopupButton(custom_text[0], size=(len(custom_text[0]), 1), button_color=button_color, focus=True,
                            bind_return_key=True)]]
        else:
            layout += [[PopupButton(custom_text[0], button_color=button_color, focus=True, bind_return_key=True,
                                    size=(len(custom_text[0]), 1)),
                        PopupButton(custom_text[1], button_color=button_color, size=(len(custom_text[1]), 1))]]
    elif button_type is sg.POPUP_BUTTONS_YES_NO:
        layout += [[PopupButton('Yes', button_color=button_color, focus=True, bind_return_key=True, pad=((0, 0), 0),
                                size=(5, 1)), PopupButton('No', button_color=button_color, size=(5, 1))]]
    elif button_type is sg.POPUP_BUTTONS_CANCELLED:
        layout += [[
            PopupButton('Cancelled', button_color=button_color, focus=True, bind_return_key=True, pad=((0, 0), 0))]]
    elif button_type is sg.POPUP_BUTTONS_ERROR:
        layout += [[PopupButton('Error', size=(6, 1), button_color=button_color, focus=True, bind_return_key=True,
                                pad=((0, 0), 0))]]
    elif button_type is sg.POPUP_BUTTONS_OK_CANCEL:
        layout += [[PopupButton('OK', size=(6, 1), button_color=button_color, focus=True, bind_return_key=True),
                    PopupButton('Cancel', size=(6, 1), button_color=button_color)]]
    elif button_type is sg.POPUP_BUTTONS_NO_BUTTONS:
        pass
    else:
        layout += [[PopupButton('OK', size=(5, 1), button_color=button_color, focus=True, bind_return_key=True,
                                pad=((0, 0), 0))]]

    window = sg.Window(_title, layout, auto_size_text=True, background_color=background_color,
                       button_color=button_color,
                       auto_close=auto_close, auto_close_duration=auto_close_duration, icon=icon, font=font,
                       no_titlebar=no_titlebar, grab_anywhere=grab_anywhere, keep_on_top=keep_on_top, location=location,
                       relative_location=relative_location, return_keyboard_events=any_key_closes,
                       modal=modal, margins=margins, disable_close=disable_close,
                       element_justification=element_justification)

    if non_blocking:
        button, values = window.read(timeout=0)
    else:
        button, values = window.read()
        window.close()
        del window

    return button

# application_start()

sg.theme('Reddit')

LogOrReg = [
    [sg.Button('Registrate'), sg.Button('Login'), sg.Button('Exit')]
]

RegistrateMenu = [[sg.Text('Enter login'), sg.Text(size=(15, 1))],
                  [sg.Input(key='-InLogin-')],
                  [sg.Text('Enter password'), sg.Text(size=(15, 1))],
                  [sg.Input(key='-InPass-')],
                  [sg.Button('Registrate'), sg.Button('Exit')]]

NewConversationMenu = [
    [sg.Text("All users:")],
    [sg.Listbox(size=(10, 10), values=[])],
    [sg.Text("Enter IDs of users you want to chat with:")],
    [sg.Input(key='InId')],
    [sg.Button('Create'), sg.Button('Return'), sg.Button('Exit')]
]

LoginMenu = [[sg.Text('Enter login'), sg.Text(size=(15, 1))],
             [sg.Input(key='-InLogin-')],
             [sg.Text('Enter password'), sg.Text(size=(15, 1))],
             [sg.Input(key='-InPass-')],
             [sg.Button('Login'), sg.Button('Exit')]]

ChatWindow = [[sg.Text('Your output will go here', size=(40, 1))],
              [sg.Output(size=(110, 20))],
              [sg.Multiline(size=(70, 5), enter_submits=False, key='-QUERY-', do_not_clear=False),
               sg.Button('Send', button_color=(sg.YELLOWS[0], sg.BLUES[0]), bind_return_key=True),
               sg.Button('Return', button_color=(sg.YELLOWS[0], sg.BLUES[0]), bind_return_key=True),
               sg.Button('Exit', button_color=(sg.YELLOWS[0], sg.GREENS[0]))]]

MessengerWindow = [
    [sg.Frame('Messages', [[sg.Frame('', [[sg.Text('BOSS:', enable_events=True, key='ClickOnName'),
                                           sg.Text('Im here', enable_events=True, key='ClickOnChat',
                                                   size=(100, 1))]])]], border_width=5, font=('Times New Roman', 12),
              size=(250, 70))],
    [sg.Button('Exit')]
]

# MessengerWindow = [[sg.Text('BOSS:', key='ClickOnChat1', enable_events=True)]]

window = sg.Window('Chat', LogOrReg)

while True:  # Event Loop
    event, values = window.read()
    # print(event, values)

    if event == sg.WIN_CLOSED or event == 'Exit':
        window.close()
        sys.exit()

    if event == 'Registrate':
        window.close()

        window = sg.Window('Chat', RegistrateMenu)
        while True:

            event, values = window.read()

            if event == sg.WIN_CLOSED or event == 'Exit':
                window.close()
                sys.exit()

            if event == 'Registrate':

                login = ''
                password = ''
                MyId = 0
                client.send('reg'.encode(MYFORMAT))

                login = ""
                for i in values['-InLogin-']:
                    login += str(i)

                NumpyInt = numpy.int64(len(login.encode(MYFORMAT)))
                client.send(NumpyInt.tobytes())
                client.send(login.encode(MYFORMAT))

                password = ""
                for i in values['-InPass-']:
                    password += str(i)

                NumpyInt = numpy.int64(len(password.encode(MYFORMAT)))
                client.send(NumpyInt.tobytes())
                client.send(password.encode(MYFORMAT))
                check = client.recv(7).decode(MYFORMAT)

                if check == "success":
                    sz = numpy.frombuffer(client.recv(8), dtype=numpy.int64)
                    MyId = sz.item()
                    getFile(client, login)
                    os.mkdir('Conversations')
                    sz = numpy.frombuffer(client.recv(8), dtype=numpy.int64)
                    UserMap = client.recv(sz.item())
                    while len(UserMap) < sz:
                        UserMap += client.recv(sz.item() - len(UserMap))
                    UserMap = ast.literal_eval(UserMap.decode(MYFORMAT))

                    window.close()
                    save_keys = []
                    save_data = []

                    MessengerWindow.clear()

                    for i, j in AllConversations.items():
                        nick = ""
                        if i[1] == "default":
                            for n in AllConversationsUsers[i]:
                                if n[0] != MyId:
                                    nick = n[2]
                                    break

                            save_keys.append(str(i))
                            create_key = []
                            for k in range(3):
                                save_data.append(str(str(i) + str(k)))
                                create_key.append(str(str(i) + str(k)))
                            if len(j) == 0:
                                MessengerWindow.append([sg.Frame(nick,
                                                                 [[
                                                                     sg.Input(str(i), key='SaveData',
                                                                              disabled=True, visible=False),
                                                                     sg.Text('', enable_events=True,
                                                                             key=create_key[0], size=(5, 2)),
                                                                     sg.Text('', enable_events=True,
                                                                             key=create_key[1], size=(16, 2)),
                                                                     sg.Text('',
                                                                             enable_events=True,
                                                                             key=create_key[2], size=(8, 2))
                                                                 ]], border_width=3, font=('Times New Roman', 14))
                                                        ])
                            else:
                                MessengerWindow.append([sg.Frame(nick,
                                                                 [[
                                                                     sg.Input(str(i), key='SaveData',
                                                                              disabled=True, visible=False),
                                                                     sg.Text(j[0][1], enable_events=True,
                                                                             key=create_key[0], size=(5, 2)),
                                                                     sg.Text(j[0][3], enable_events=True,
                                                                             key=create_key[1], size=(16, 2)),
                                                                     sg.Text(
                                                                         str(((j[0][4].split(".")[0].split(
                                                                             ' '))[::-1])[0]) + "\n" + str(
                                                                             ((j[0][
                                                                                   4].split(
                                                                                 ".")[0].split(' '))[::-1])[
                                                                                 1]),
                                                                         enable_events=True,
                                                                         key=create_key[2], size=(8, 2))
                                                                 ]], border_width=3, font=('Times New Roman', 14))
                                                        ])

                        else:
                            save_keys.append(str(i))
                            create_key = []
                            for k in range(3):
                                save_data.append(str(str(i) + str(k)))
                                create_key.append(str(str(i) + str(k)))

                            if len(j) == 0:
                                MessengerWindow.append([sg.Frame(str(i[1]),
                                                                 [[
                                                                     sg.Input(str(i), key='SaveData',
                                                                              disabled=True, visible=False),
                                                                     sg.Text('', enable_events=True,
                                                                             key=create_key[0], size=(5, 2)),
                                                                     sg.Text('', enable_events=True,
                                                                             key=create_key[1], size=(16, 2)),
                                                                     sg.Text('',
                                                                             enable_events=True,
                                                                             key=create_key[2], size=(8, 2))
                                                                 ]], border_width=3, font=('Times New Roman', 14))
                                                        ])
                            else:
                                MessengerWindow.append([sg.Frame(str(i[1]),
                                                                 [[
                                                                     sg.Input(str(i), key='SaveData',
                                                                              disabled=True, visible=False),
                                                                     sg.Text(j[0][1], enable_events=True,
                                                                             key=create_key[0], size=(5, 2)),
                                                                     sg.Text(j[0][3], enable_events=True,
                                                                             key=create_key[1], size=(16, 2)),
                                                                     sg.Text(
                                                                         str(((j[0][4].split(".")[0].split(
                                                                             ' '))[::-1])[0]) + "\n" + str(
                                                                             ((j[0][
                                                                                   4].split(
                                                                                 ".")[0].split(' '))[::-1])[
                                                                                 1]),
                                                                         enable_events=True,
                                                                         key=create_key[2], size=(8, 2))
                                                                 ]], border_width=3, font=('Times New Roman', 14))
                                                        ])

                    MessengerWindow = [[sg.Frame('Messages', [
                        [sg.Column(MessengerWindow, scrollable=True, size=(300, 200), vertical_scroll_only=True)]],
                                                 border_width=5, font=('Times New Roman', 24))]]
                    MessengerWindow.append([sg.Button('Write a new message'), sg.Button('Exit')])
                    window = sg.Window('Chat', MessengerWindow, finalize=True)

                    GetMessageThreadInWindow = threading.Thread(target=getMessageInWindow, args=(client,))
                    GetMessageThreadInWindow.start()

                    while True:
                        event, values = window.read(1)

                        # sv = values['SaveData']
                        if event == sg.WIN_CLOSED or event == 'Exit':
                            window.close()
                            sys.exit()

                        if event == 'Write a new message':

                            window.close()

                            NewConversationMenu.clear()

                            arr = []
                            for i in UserMap:
                                arr.append(str("ID:  " + str(i[0]) + "      User Name:  " + str(i[2])))

                            NewConversationMenu = [
                                [sg.Text("All users:")],
                                [sg.Listbox(size=(30, 8), values=arr)],
                                [sg.Text("Enter space-separated IDs of users you want to chat with:")],
                                [sg.Input(key='InId')],
                                [sg.Text(
                                    "Enter name of conversation:\n(if this is a two-person conversation, enter:default)")],
                                [sg.Input(key='InNameConv')],
                                [sg.Button('Create'), sg.Button('Return'), sg.Button('Exit')]
                            ]

                            window = sg.Window('Chat', NewConversationMenu)

                            while True:

                                event, values = window.read(1)

                                if event == sg.WIN_CLOSED or event == 'Exit':
                                    window.close()
                                    sys.exit()

                                if event == 'Create':

                                    ConvName = ""
                                    for i in values['InNameConv']:
                                        ConvName += str(i)
                                    save_convname = ConvName

                                    ConvUsers = ""
                                    for i in values['InId']:
                                        ConvUsers += str(i)
                                    ConvUsers = ConvUsers + " " + str(MyId)

                                    check_conv_users = list(map(int, (ConvUsers.split(' '))))

                                    flag_check = True

                                    if save_convname == "default":
                                        if len(check_conv_users) != 2:
                                            flag_check = False
                                            popupBoi("You can't create conversation with two users and name it default",
                                                     title='Notification',
                                                     keep_on_top=True, margins=(50, 10),
                                                     disable_close=False, element_justification='c')
                                        else:
                                            for i in AllConversationsUsers:
                                                mass = []
                                                if i[1] == 'default':
                                                    for j in AllConversationsUsers[i]:
                                                        mass.append(j[0])
                                                    if (check_conv_users[0] in mass) and (check_conv_users[1] in mass):
                                                        flag_check = False
                                                        popupBoi('Such a conversation already exists',
                                                                 title='Notification',
                                                                 keep_on_top=True, margins=(50, 10),
                                                                 disable_close=False, element_justification='c')
                                                        break

                                    else:
                                        for i in AllConversationsUsers:
                                            if i[1] == save_convname:
                                                flag_check = False
                                                popupBoi('Such a conversation already exists, rename it',
                                                         title='Notification',
                                                         keep_on_top=True, margins=(50, 10),
                                                         disable_close=False, element_justification='c')

                                    if flag_check:
                                        client.send('conv'.encode(MYFORMAT))
                                        ConvName = ConvName.encode(MYFORMAT)
                                        ConvUsers = str(list(map(int, (ConvUsers.split(' '))))).encode(MYFORMAT)
                                        NumpyInt = numpy.int64(len(ConvName))
                                        client.send(NumpyInt.tobytes())
                                        client.send(ConvName)
                                        NumpyInt = numpy.int64(len(ConvUsers))
                                        client.send(NumpyInt.tobytes())
                                        client.send(ConvUsers)
                                        popupBoi('Conversation was created!', title='Notification',
                                                 keep_on_top=True, margins=(50, 10),
                                                 disable_close=False, element_justification='c')

                                if event == 'Return':
                                    window.close()
                                    save_keys = []
                                    save_data = []

                                    MessengerWindow.clear()

                                    for i, j in AllConversations.items():
                                        nick = ""
                                        if i[1] == "default":
                                            for n in AllConversationsUsers[i]:
                                                if n[0] != MyId:
                                                    nick = n[2]
                                                    break

                                            save_keys.append(str(i))
                                            create_key = []
                                            for k in range(3):
                                                save_data.append(str(str(i) + str(k)))
                                                create_key.append(str(str(i) + str(k)))
                                            if len(j) == 0:
                                                MessengerWindow.append([sg.Frame(nick,
                                                                                 [[
                                                                                     sg.Input(str(i), key='SaveData',
                                                                                              disabled=True,
                                                                                              visible=False),
                                                                                     sg.Text('', enable_events=True,
                                                                                             key=create_key[0],
                                                                                             size=(5, 2)),
                                                                                     sg.Text('', enable_events=True,
                                                                                             key=create_key[1],
                                                                                             size=(16, 2)),
                                                                                     sg.Text('',
                                                                                             enable_events=True,
                                                                                             key=create_key[2],
                                                                                             size=(8, 2))
                                                                                 ]], border_width=3,
                                                                                 font=('Times New Roman', 14))
                                                                        ])
                                            else:
                                                MessengerWindow.append([sg.Frame(nick,
                                                                                 [[
                                                                                     sg.Input(str(i), key='SaveData',
                                                                                              disabled=True,
                                                                                              visible=False),
                                                                                     sg.Text(j[0][1],
                                                                                             enable_events=True,
                                                                                             key=create_key[0],
                                                                                             size=(5, 2)),
                                                                                     sg.Text(j[0][3],
                                                                                             enable_events=True,
                                                                                             key=create_key[1],
                                                                                             size=(16, 2)),
                                                                                     sg.Text(
                                                                                         str(((j[0][4].split(".")[
                                                                                             0].split(
                                                                                             ' '))[::-1])[
                                                                                                 0]) + "\n" + str(
                                                                                             ((j[0][
                                                                                                   4].split(
                                                                                                 ".")[0].split(' '))[
                                                                                              ::-1])[
                                                                                                 1]),
                                                                                         enable_events=True,
                                                                                         key=create_key[2], size=(8, 2))
                                                                                 ]], border_width=3,
                                                                                 font=('Times New Roman', 14))
                                                                        ])

                                        else:
                                            save_keys.append(str(i))
                                            create_key = []
                                            for k in range(3):
                                                save_data.append(str(str(i) + str(k)))
                                                create_key.append(str(str(i) + str(k)))

                                            if len(j) == 0:
                                                MessengerWindow.append([sg.Frame(str(i[1]),
                                                                                 [[
                                                                                     sg.Input(str(i), key='SaveData',
                                                                                              disabled=True,
                                                                                              visible=False),
                                                                                     sg.Text('', enable_events=True,
                                                                                             key=create_key[0],
                                                                                             size=(5, 2)),
                                                                                     sg.Text('', enable_events=True,
                                                                                             key=create_key[1],
                                                                                             size=(16, 2)),
                                                                                     sg.Text('',
                                                                                             enable_events=True,
                                                                                             key=create_key[2],
                                                                                             size=(8, 2))
                                                                                 ]], border_width=3,
                                                                                 font=('Times New Roman', 14))
                                                                        ])
                                            else:
                                                MessengerWindow.append([sg.Frame(str(i[1]),
                                                                                 [[
                                                                                     sg.Input(str(i), key='SaveData',
                                                                                              disabled=True,
                                                                                              visible=False),
                                                                                     sg.Text(j[0][1],
                                                                                             enable_events=True,
                                                                                             key=create_key[0],
                                                                                             size=(5, 2)),
                                                                                     sg.Text(j[0][3],
                                                                                             enable_events=True,
                                                                                             key=create_key[1],
                                                                                             size=(16, 2)),
                                                                                     sg.Text(
                                                                                         str(((j[0][4].split(".")[
                                                                                             0].split(
                                                                                             ' '))[::-1])[
                                                                                                 0]) + "\n" + str(
                                                                                             ((j[0][
                                                                                                   4].split(
                                                                                                 ".")[0].split(' '))[
                                                                                              ::-1])[
                                                                                                 1]),
                                                                                         enable_events=True,
                                                                                         key=create_key[2], size=(8, 2))
                                                                                 ]], border_width=3,
                                                                                 font=('Times New Roman', 14))
                                                                        ])

                                    MessengerWindow = [[sg.Frame('Messages', [[sg.Column(MessengerWindow,
                                                                                         scrollable=True,
                                                                                         size=(300, 200),
                                                                                         vertical_scroll_only=True)]],
                                                                 border_width=5, font=('Times New Roman', 24))]]
                                    MessengerWindow.append([sg.Button('Write a new message'), sg.Button('Exit')])
                                    window = sg.Window('Chat', MessengerWindow, finalize=True)
                                    break

                        for i in save_data:
                            if event == i:

                                sv = ""
                                for j in values['SaveData']:
                                    sv += str(j)

                                window.close()

                                sv = str(i)
                                ln = len(sv)
                                sv = sv[:ln - 1]

                                sv = ast.literal_eval(sv)

                                ChatWindow.clear()
                                arr = []
                                for i in reversed(AllConversations[sv]):
                                    arr.append(str(i[1]) + "  :  " + str(i[3]) + "        " + str(
                                        ((i[4].split(".")[0].split(' '))[::-1])[0]) + " " + str(
                                        ((i[4].split(".")[0].split(' '))[::-1])[1]))

                                ChatWindow = [
                                    [sg.Listbox(size=(90, 22), key='chat', values=arr, horizontal_scroll=True)],
                                    [sg.InputText(key='input', size=(25, 10)),
                                     sg.Button('Send', bind_return_key=True, size=(9, 1)),
                                     sg.Button('Return', size=(9, 1)),
                                     sg.Button('Exit', size=(9, 1))],
                                ]

                                window = sg.Window('Chat', ChatWindow, finalize=True)
                                window['chat'].Widget.yview_moveto(1.0)

                                # GetMessageThread = threading.Thread(target=getMessage, args=(client,))
                                # GetMessageThread.start()
                                while True:

                                    event, values = window.read(1)

                                    # SendRequestThread = threading.Thread(target=sendRequestCheck,
                                    #                                      args=(client, login, MyId))
                                    # SendRequestThread.start()

                                    if event == sg.WIN_CLOSED or event == 'Exit':
                                        window.close()
                                        sys.exit()

                                    if event == 'Send':
                                        # global AllConversations, AllConversationsUsers, UserMap, MYFORMAT
                                        while True:
                                            # print('Type of request?')
                                            # request = input()

                                            request = "send"
                                            client.send(request.encode(MYFORMAT))

                                            if request == "send":
                                                window["input"].update('')
                                                # print('Conversation number?')
                                                # ConversationNumber = int(input())
                                                ConversationNumber = sv[0]
                                                NumpyInt = numpy.int64(ConversationNumber)
                                                client.send(NumpyInt.tobytes())

                                                # print('TypeOfSend?')
                                                # TypeOfSend = int(input())

                                                Message = ""
                                                for i in values['input']:
                                                    Message += i

                                                TypeOfSend = 1
                                                Type = numpy.int64(TypeOfSend)
                                                if TypeOfSend == 1:
                                                    # print('Enter message')

                                                    TextToSend = Message.encode(MYFORMAT)
                                                    NumpyInt = numpy.int64(len(TextToSend))
                                                    client.send(Type.tobytes())
                                                    client.send(NumpyInt.tobytes())
                                                    client.send(TextToSend)
                                                    window['chat'].Widget.yview_moveto(1.0)
                                                    break

                                                if TypeOfSend == 2:
                                                    # print('Enter path to file')
                                                    MyPath = input()
                                                    if os.path.isfile(MyPath):
                                                        client.send(Type.tobytes())
                                                        FileName = os.path.basename(MyPath)
                                                        sendFile(client, MyPath, FileName)
                                                    # else:
                                                    # print('Something is wrong and you know it')
                                                if TypeOfSend == 3:
                                                    # print('Enter message')
                                                    TextToSend = input().encode(MYFORMAT)
                                                    NumpyInt = numpy.int64(len(TextToSend))
                                                    # print('Enter path to file')
                                                    MyPath = input()
                                                    if os.path.isfile(MyPath):
                                                        client.send(Type.tobytes())
                                                        client.send(NumpyInt.tobytes())
                                                        client.send(TextToSend)
                                                        FileName = os.path.basename(MyPath)
                                                        sendFile(client, MyPath, FileName)

                                                #     else:
                                                #         print('Something is wrong and you know it')
                                                # print("Беседа и все ее сообщения")
                                                # print(AllConversations, sep="\n")
                                                # print("Беседа и user данные ее участников", sep="\n")
                                                # print(AllConversationsUsers)

                                    if event == 'Return':
                                        window.close()
                                        save_keys = []
                                        save_data = []

                                        MessengerWindow.clear()

                                        for i, j in AllConversations.items():
                                            nick = ""
                                            if i[1] == "default":
                                                for n in AllConversationsUsers[i]:
                                                    if n[0] != MyId:
                                                        nick = n[2]
                                                        break

                                                save_keys.append(str(i))
                                                create_key = []
                                                for k in range(3):
                                                    save_data.append(str(str(i) + str(k)))
                                                    create_key.append(str(str(i) + str(k)))
                                                if len(j) == 0:
                                                    MessengerWindow.append([sg.Frame(nick,
                                                                                     [[
                                                                                         sg.Input(str(i),
                                                                                                  key='SaveData',
                                                                                                  disabled=True,
                                                                                                  visible=False),
                                                                                         sg.Text('', enable_events=True,
                                                                                                 key=create_key[0],
                                                                                                 size=(5, 2)),
                                                                                         sg.Text('', enable_events=True,
                                                                                                 key=create_key[1],
                                                                                                 size=(16, 2)),
                                                                                         sg.Text('',
                                                                                                 enable_events=True,
                                                                                                 key=create_key[2],
                                                                                                 size=(8, 2))
                                                                                     ]], border_width=3,
                                                                                     font=('Times New Roman', 14))
                                                                            ])
                                                else:
                                                    MessengerWindow.append([sg.Frame(nick,
                                                                                     [[
                                                                                         sg.Input(str(i),
                                                                                                  key='SaveData',
                                                                                                  disabled=True,
                                                                                                  visible=False),
                                                                                         sg.Text(j[0][1],
                                                                                                 enable_events=True,
                                                                                                 key=create_key[0],
                                                                                                 size=(5, 2)),
                                                                                         sg.Text(j[0][3],
                                                                                                 enable_events=True,
                                                                                                 key=create_key[1],
                                                                                                 size=(16, 2)),
                                                                                         sg.Text(
                                                                                             str(((j[0][4].split(".")[
                                                                                                 0].split(
                                                                                                 ' '))[::-1])[
                                                                                                     0]) + "\n" + str(
                                                                                                 ((j[0][
                                                                                                     4].split(
                                                                                                     ".")[0].split(
                                                                                                     ' '))[::-1])[
                                                                                                     1]),
                                                                                             enable_events=True,
                                                                                             key=create_key[2],
                                                                                             size=(8, 2))
                                                                                     ]], border_width=3,
                                                                                     font=('Times New Roman', 14))
                                                                            ])

                                            else:
                                                save_keys.append(str(i))
                                                create_key = []
                                                for k in range(3):
                                                    save_data.append(str(str(i) + str(k)))
                                                    create_key.append(str(str(i) + str(k)))

                                                if len(j) == 0:
                                                    MessengerWindow.append([sg.Frame(str(i[1]),
                                                                                     [[
                                                                                         sg.Input(str(i),
                                                                                                  key='SaveData',
                                                                                                  disabled=True,
                                                                                                  visible=False),
                                                                                         sg.Text('', enable_events=True,
                                                                                                 key=create_key[0],
                                                                                                 size=(5, 2)),
                                                                                         sg.Text('', enable_events=True,
                                                                                                 key=create_key[1],
                                                                                                 size=(16, 2)),
                                                                                         sg.Text('',
                                                                                                 enable_events=True,
                                                                                                 key=create_key[2],
                                                                                                 size=(8, 2))
                                                                                     ]], border_width=3,
                                                                                     font=('Times New Roman', 14))
                                                                            ])
                                                else:
                                                    MessengerWindow.append([sg.Frame(str(i[1]),
                                                                                     [[
                                                                                         sg.Input(str(i),
                                                                                                  key='SaveData',
                                                                                                  disabled=True,
                                                                                                  visible=False),
                                                                                         sg.Text(j[0][1],
                                                                                                 enable_events=True,
                                                                                                 key=create_key[0],
                                                                                                 size=(5, 2)),
                                                                                         sg.Text(j[0][3],
                                                                                                 enable_events=True,
                                                                                                 key=create_key[1],
                                                                                                 size=(16, 2)),
                                                                                         sg.Text(
                                                                                             str(((j[0][4].split(".")[
                                                                                                 0].split(
                                                                                                 ' '))[::-1])[
                                                                                                     0]) + "\n" + str(
                                                                                                 ((j[0][
                                                                                                     4].split(
                                                                                                     ".")[0].split(
                                                                                                     ' '))[::-1])[
                                                                                                     1]),
                                                                                             enable_events=True,
                                                                                             key=create_key[2],
                                                                                             size=(8, 2))
                                                                                     ]], border_width=3,
                                                                                     font=('Times New Roman', 14))
                                                                            ])

                                        MessengerWindow = [[sg.Frame('Messages', [[sg.Column(MessengerWindow,
                                                                                             scrollable=True,
                                                                                             size=(300, 200),
                                                                                             vertical_scroll_only=True)]],
                                                                     border_width=5, font=('Times New Roman', 24))]]
                                        MessengerWindow.append([sg.Button('Write a new message'), sg.Button('Exit')])
                                        window = sg.Window('Chat', MessengerWindow, finalize=True)
                                        break

                else:
                    # print('Such user is already exists')
                    popupBoi('There is no such user or password is wrong', title='Notification', keep_on_top=True,
                             margins=(50, 10),
                             disable_close=False, element_justification='c')
                    continue

    if event == 'Login':

        window.close()

        window = sg.Window('Chat', LoginMenu)

        # print('Enter login')
        # login = input('Enter login')
        while True:
            event, values = window.read()

            if event == sg.WIN_CLOSED or event == 'Exit':
                window.close()
                sys.exit()

            if event == 'Login':

                login = ''
                password = ''
                MyId = 0
                client.send('log'.encode(MYFORMAT))

                login = ""
                for i in values['-InLogin-']:
                    login += str(i)

                NumpyInt = numpy.int64(len(login.encode(MYFORMAT)))
                client.send(NumpyInt.tobytes())
                client.send(login.encode(MYFORMAT))
                # print('Enter_password')
                # password = input('Enter_password')

                password = ""
                for i in values['-InPass-']:
                    password += str(i)

                NumpyInt = numpy.int64(len(password.encode(MYFORMAT)))
                client.send(NumpyInt.tobytes())
                client.send(password.encode(MYFORMAT))
                check = client.recv(7).decode(MYFORMAT)

                if check == 'success':
                    NumpyInt = numpy.frombuffer(client.recv(8), dtype=numpy.int64)
                    MyId = NumpyInt.item()
                    # print(f'My id is {MyId} and my nick is {login}')
                    # getFile(client, login)

                    ConversationPhoto = dict()
                    UsersPhoto = dict()

                    sz = numpy.frombuffer(client.recv(8), dtype=numpy.int64)
                    UserMap = client.recv(sz.item())
                    while len(UserMap) < sz:
                        UserMap += client.recv(sz.item() - len(UserMap))
                    UserMap = ast.literal_eval(UserMap.decode(MYFORMAT))

                    sz = numpy.frombuffer(client.recv(8), dtype=numpy.int64)
                    AllConversations = client.recv(sz.item())
                    while len(AllConversations) < sz:
                        AllConversations += client.recv(sz.item() - len(AllConversations))
                    AllConversations = ast.literal_eval(AllConversations.decode(MYFORMAT))

                    sz = numpy.frombuffer(client.recv(8), dtype=numpy.int64)
                    AllConversationsUsers = client.recv(sz.item())
                    while len(AllConversationsUsers) < sz:
                        AllConversationsUsers += client.recv(sz.item() - len(AllConversationsUsers))
                    AllConversationsUsers = ast.literal_eval(AllConversationsUsers.decode(MYFORMAT))

                    sz = numpy.frombuffer(client.recv(8), dtype=numpy.int64)
                    ConversationPhoto = client.recv(sz.item())
                    while len(ConversationPhoto) < sz:
                        ConversationPhoto += client.recv(sz.item() - len(ConversationPhoto))
                    ConversationPhoto = ast.literal_eval(ConversationPhoto.decode(MYFORMAT))

                    sz = numpy.frombuffer(client.recv(8), dtype=numpy.int64)
                    UsersPhoto = client.recv(sz.item())
                    while len(UsersPhoto) < sz:
                        UsersPhoto += client.recv(sz.item() - len(UsersPhoto))
                    UsersPhoto = ast.literal_eval(UsersPhoto.decode(MYFORMAT))

                    os.mkdir('Conversations')
                    for conversations, data in ConversationPhoto.items():
                        if conversations[1] != 'default':
                            MyPath = os.path.join(BASE_DIR, 'Conversations' + '\\' + str(conversations[1]))
                            os.mkdir(MyPath)
                            MyPath = os.path.join(BASE_DIR,
                                                  'Conversations' + '\\' + str(conversations[1]) + "\\" + str(data[0]))
                            file = open(MyPath, 'wb')
                            file.write(data[1])
                            file.close

                    os.mkdir('Users')
                    for user, data in UsersPhoto.items():
                        MyPath = os.path.join(BASE_DIR, 'Users' + '\\' + str(user[2]))
                        os.mkdir(MyPath)
                        MyPath = os.path.join(BASE_DIR, 'Users' + '\\' + str(user[2]) + '\\' + str(data[0]))
                        file = open(MyPath, 'wb')
                        file.write(data[1])
                        file.close

                    window.close()
                    save_keys = []
                    save_data = []

                    MessengerWindow.clear()

                    for i, j in AllConversations.items():
                        nick = ""
                        if i[1] == "default":
                            for n in AllConversationsUsers[i]:
                                if n[0] != MyId:
                                    nick = n[2]
                                    break

                            save_keys.append(str(i))
                            create_key = []
                            for k in range(3):
                                save_data.append(str(str(i) + str(k)))
                                create_key.append(str(str(i) + str(k)))
                            if len(j) == 0:
                                MessengerWindow.append([sg.Frame(nick,
                                                                            [[
                                                                                sg.Input(str(i), key='SaveData',
                                                                                         disabled=True, visible=False),
                                                                                sg.Text('', enable_events=True,
                                                                                        key=create_key[0], size=(5,2)),
                                                                                sg.Text('', enable_events=True,
                                                                                        key=create_key[1], size=(16,2)),
                                                                                sg.Text('',
                                                                                        enable_events=True,
                                                                                        key=create_key[2], size=(8,2))
                                                                            ]], border_width=3, font=('Times New Roman', 14))
                                                                   ])
                            else:
                                MessengerWindow.append([sg.Frame(nick,
                                                                            [[
                                                                                sg.Input(str(i), key='SaveData',
                                                                                         disabled=True, visible=False),
                                                                                sg.Text(j[0][1], enable_events=True,
                                                                                        key=create_key[0], size=(5,2)),
                                                                                sg.Text(j[0][3], enable_events=True,
                                                                                        key=create_key[1], size=(16,2)),
                                                                                sg.Text(
                                                                                    str(((j[0][4].split(".")[0].split(
                                                                                        ' '))[::-1])[0]) + "\n" + str(
                                                                                        ((j[0][
                                                                                              4].split(
                                                                                            ".")[0].split(' '))[::-1])[
                                                                                            1]),
                                                                                    enable_events=True,
                                                                                    key=create_key[2], size=(8,2))
                                                                            ]], border_width=3, font=('Times New Roman', 14))
                                                                   ])
                                # MessengerWindow.append([sg.Text("Arbuzi"), sg.Text("Arbuzi"),sg.Text("Arbuzi"),sg.Text("Arbuzi")])

                        else:
                            save_keys.append(str(i))
                            create_key = []
                            for k in range(3):
                                save_data.append(str(str(i) + str(k)))
                                create_key.append(str(str(i) + str(k)))

                            if len(j) == 0:
                                MessengerWindow.append([sg.Frame(str(i[1]),
                                                                            [[
                                                                                sg.Input(str(i), key='SaveData',
                                                                                         disabled=True, visible=False),
                                                                                sg.Text('', enable_events=True,
                                                                                        key=create_key[0], size=(5,2)),
                                                                                sg.Text('', enable_events=True,
                                                                                        key=create_key[1], size=(16,2)),
                                                                                sg.Text('',
                                                                                        enable_events=True,
                                                                                        key=create_key[2], size=(8,2))
                                                                            ]], border_width=3, font=('Times New Roman', 14))
                                                                   ])
                            else:
                                MessengerWindow.append([sg.Frame(str(i[1]),
                                                                            [[
                                                                                sg.Input(str(i), key='SaveData',
                                                                                         disabled=True, visible=False),
                                                                                sg.Text(j[0][1], enable_events=True,
                                                                                        key=create_key[0], size=(5,2)),
                                                                                sg.Text(j[0][3], enable_events=True,
                                                                                        key=create_key[1], size=(16,2)),
                                                                                sg.Text(
                                                                                    str(((j[0][4].split(".")[0].split(
                                                                                        ' '))[::-1])[0]) + "\n" + str(
                                                                                        ((j[0][
                                                                                              4].split(
                                                                                            ".")[0].split(' '))[::-1])[
                                                                                            1]),
                                                                                    enable_events=True,
                                                                                    key=create_key[2], size=(8,2))
                                                                            ]], border_width=3, font=('Times New Roman', 14))
                                                                   ])

                    MessengerWindow = [[sg.Frame('Messages',[[sg.Column(MessengerWindow, scrollable=True, size=(300,200), vertical_scroll_only=True)]], border_width=5, font=('Times New Roman', 24))]]
                    MessengerWindow.append([sg.Button('Write a new message'), sg.Button('Exit')])
                    window = sg.Window('Chat', MessengerWindow, finalize=True)

                    GetMessageThreadInWindow = threading.Thread(target=getMessageInWindow, args=(client,))
                    GetMessageThreadInWindow.start()

                    while True:
                        event, values = window.read(1)

                        # sv = values['SaveData']
                        if event == sg.WIN_CLOSED or event == 'Exit':
                            window.close()
                            sys.exit()

                        if event == 'Write a new message':

                            window.close()

                            NewConversationMenu.clear()

                            arr = []
                            for i in UserMap:
                                arr.append(str("ID:  " + str(i[0]) + "      User Name:  " + str(i[2])))

                            NewConversationMenu = [
                                [sg.Text("All users:")],
                                [sg.Listbox(size=(30, 8), values=arr)],
                                [sg.Text("Enter space-separated IDs of users you want to chat with:")],
                                [sg.Input(key='InId')],
                                [sg.Text("Enter name of conversation:\n(if this is a two-person conversation, enter:default)")],
                                [sg.Input(key='InNameConv')],
                                [sg.Button('Create'), sg.Button('Return'), sg.Button('Exit')]
                            ]

                            window = sg.Window('Chat', NewConversationMenu)

                            while True:

                                event, values = window.read(1)

                                if event == sg.WIN_CLOSED or event == 'Exit':
                                    window.close()
                                    sys.exit()

                                if event == 'Create':

                                    ConvName = ""
                                    for i in values['InNameConv']:
                                        ConvName += str(i)
                                    save_convname = ConvName

                                    
                                    ConvUsers = ""
                                    for i in values['InId']:
                                        ConvUsers += str(i)
                                    ConvUsers = ConvUsers + " " + str(MyId)

                                    check_conv_users = list(map(int, (ConvUsers.split(' '))))

                                    flag_check = True

                                    if save_convname == "default":
                                        if len(check_conv_users) != 2:
                                            flag_check = False
                                            popupBoi("You can't create conversation with two users and name it default", title='Notification',
                                                     keep_on_top=True, margins=(50, 10),
                                                     disable_close=False, element_justification='c')
                                        else:
                                            for i in AllConversationsUsers:
                                                mass = []
                                                if i[1] == 'default':
                                                    for j in AllConversationsUsers[i]:
                                                        mass.append(j[0])
                                                    if (check_conv_users[0] in mass) and (check_conv_users[1] in mass):
                                                        flag_check = False
                                                        popupBoi('Such a conversation already exists',
                                                                 title='Notification',
                                                                 keep_on_top=True, margins=(50, 10),
                                                                 disable_close=False, element_justification='c')
                                                        break

                                    else:
                                        for i in AllConversationsUsers:
                                            if i[1] == save_convname:
                                                flag_check = False
                                                popupBoi('Such a conversation already exists, rename it',
                                                         title='Notification',
                                                         keep_on_top=True, margins=(50, 10),
                                                         disable_close=False, element_justification='c')

                                    if flag_check:
                                        client.send('conv'.encode(MYFORMAT))
                                        ConvName = ConvName.encode(MYFORMAT)
                                        ConvUsers = str(list(map(int, (ConvUsers.split(' '))))).encode(MYFORMAT)
                                        NumpyInt = numpy.int64(len(ConvName))
                                        client.send(NumpyInt.tobytes())
                                        client.send(ConvName)
                                        NumpyInt = numpy.int64(len(ConvUsers))
                                        client.send(NumpyInt.tobytes())
                                        client.send(ConvUsers)
                                        popupBoi('Conversation was created!', title='Notification',
                                                 keep_on_top=True, margins=(50, 10),
                                                 disable_close=False, element_justification='c')

                                if event == 'Return':
                                    window.close()
                                    save_keys = []
                                    save_data = []

                                    MessengerWindow.clear()

                                    for i, j in AllConversations.items():
                                        nick = ""
                                        if i[1] == "default":
                                            for n in AllConversationsUsers[i]:
                                                if n[0] != MyId:
                                                    nick = n[2]
                                                    break

                                            save_keys.append(str(i))
                                            create_key = []
                                            for k in range(3):
                                                save_data.append(str(str(i) + str(k)))
                                                create_key.append(str(str(i) + str(k)))
                                            if len(j) == 0:
                                                MessengerWindow.append([sg.Frame(nick,
                                                                                 [[
                                                                                     sg.Input(str(i), key='SaveData',
                                                                                              disabled=True,
                                                                                              visible=False),
                                                                                     sg.Text('', enable_events=True,
                                                                                             key=create_key[0],
                                                                                             size=(5, 2)),
                                                                                     sg.Text('', enable_events=True,
                                                                                             key=create_key[1],
                                                                                             size=(16, 2)),
                                                                                     sg.Text('',
                                                                                             enable_events=True,
                                                                                             key=create_key[2],
                                                                                             size=(8, 2))
                                                                                 ]], border_width=3,
                                                                                 font=('Times New Roman', 14))
                                                                        ])
                                            else:
                                                MessengerWindow.append([sg.Frame(nick,
                                                                                 [[
                                                                                     sg.Input(str(i), key='SaveData',
                                                                                              disabled=True,
                                                                                              visible=False),
                                                                                     sg.Text(j[0][1],
                                                                                             enable_events=True,
                                                                                             key=create_key[0],
                                                                                             size=(5, 2)),
                                                                                     sg.Text(j[0][3],
                                                                                             enable_events=True,
                                                                                             key=create_key[1],
                                                                                             size=(16, 2)),
                                                                                     sg.Text(
                                                                                         str(((j[0][4].split(".")[
                                                                                             0].split(
                                                                                             ' '))[::-1])[
                                                                                                 0]) + "\n" + str(
                                                                                             ((j[0][
                                                                                                   4].split(
                                                                                                 ".")[0].split(' '))[
                                                                                              ::-1])[
                                                                                                 1]),
                                                                                         enable_events=True,
                                                                                         key=create_key[2], size=(8, 2))
                                                                                 ]], border_width=3,
                                                                                 font=('Times New Roman', 14))
                                                                        ])

                                        else:
                                            save_keys.append(str(i))
                                            create_key = []
                                            for k in range(3):
                                                save_data.append(str(str(i) + str(k)))
                                                create_key.append(str(str(i) + str(k)))

                                            if len(j) == 0:
                                                MessengerWindow.append([sg.Frame(str(i[1]),
                                                                                 [[
                                                                                     sg.Input(str(i), key='SaveData',
                                                                                              disabled=True,
                                                                                              visible=False),
                                                                                     sg.Text('', enable_events=True,
                                                                                             key=create_key[0],
                                                                                             size=(5, 2)),
                                                                                     sg.Text('', enable_events=True,
                                                                                             key=create_key[1],
                                                                                             size=(16, 2)),
                                                                                     sg.Text('',
                                                                                             enable_events=True,
                                                                                             key=create_key[2],
                                                                                             size=(8, 2))
                                                                                 ]], border_width=3,
                                                                                 font=('Times New Roman', 14))
                                                                        ])
                                            else:
                                                MessengerWindow.append([sg.Frame(str(i[1]),
                                                                                 [[
                                                                                     sg.Input(str(i), key='SaveData',
                                                                                              disabled=True,
                                                                                              visible=False),
                                                                                     sg.Text(j[0][1],
                                                                                             enable_events=True,
                                                                                             key=create_key[0],
                                                                                             size=(5, 2)),
                                                                                     sg.Text(j[0][3],
                                                                                             enable_events=True,
                                                                                             key=create_key[1],
                                                                                             size=(16, 2)),
                                                                                     sg.Text(
                                                                                         str(((j[0][4].split(".")[
                                                                                             0].split(
                                                                                             ' '))[::-1])[
                                                                                                 0]) + "\n" + str(
                                                                                             ((j[0][
                                                                                                   4].split(
                                                                                                 ".")[0].split(' '))[
                                                                                              ::-1])[
                                                                                                 1]),
                                                                                         enable_events=True,
                                                                                         key=create_key[2], size=(8, 2))
                                                                                 ]], border_width=3,
                                                                                 font=('Times New Roman', 14))
                                                                        ])

                                    MessengerWindow = [[sg.Frame('Messages', [[sg.Column(MessengerWindow,
                                                                                         scrollable=True,
                                                                                         size=(300, 200),
                                                                                         vertical_scroll_only=True)]],
                                                                 border_width=5, font=('Times New Roman', 24))]]
                                    MessengerWindow.append([sg.Button('Write a new message'), sg.Button('Exit')])
                                    window = sg.Window('Chat', MessengerWindow, finalize=True)
                                    break

                        for i in save_data:
                            if event == i:

                                sv = ""
                                for j in values['SaveData']:
                                    sv += str(j)

                                window.close()

                                sv = str(i)
                                ln = len(sv)
                                sv = sv[:ln - 1]

                                sv = ast.literal_eval(sv)

                                ChatWindow.clear()
                                arr = []
                                for i in reversed(AllConversations[sv]):
                                    arr.append(str(i[1]) + "  :  " + str(i[3]) + "        " + str(
                                        ((i[4].split(".")[0].split(' '))[::-1])[0]) + " " + str(
                                        ((i[4].split(".")[0].split(' '))[::-1])[1]))

                                ChatWindow = [
                                    [sg.Listbox(size=(90, 22), key='chat', values=arr, horizontal_scroll=True)],
                                    [sg.InputText(key='input', size=(25, 10)),
                                     sg.Button('Send', bind_return_key=True, size=(9, 1)),
                                     sg.Button('Return', size=(9, 1)),
                                     sg.Button('Exit', size=(9, 1))],
                                ]

                                window = sg.Window('Chat', ChatWindow, finalize=True)
                                window['chat'].Widget.yview_moveto(1.0)

                                # GetMessageThread = threading.Thread(target=getMessage, args=(client,))
                                # GetMessageThread.start()
                                while True:

                                    event, values = window.read(1)

                                    # SendRequestThread = threading.Thread(target=sendRequestCheck,
                                    #                                      args=(client, login, MyId))
                                    # SendRequestThread.start()

                                    if event == sg.WIN_CLOSED or event == 'Exit':
                                        window.close()
                                        sys.exit()

                                    if event == 'Send':
                                        # global AllConversations, AllConversationsUsers, UserMap, MYFORMAT
                                        while True:
                                            # print('Type of request?')
                                            # request = input()

                                            request = "send"
                                            client.send(request.encode(MYFORMAT))

                                            if request == "send":
                                                window["input"].update('')
                                                # print('Conversation number?')
                                                # ConversationNumber = int(input())
                                                ConversationNumber = sv[0]
                                                NumpyInt = numpy.int64(ConversationNumber)
                                                client.send(NumpyInt.tobytes())

                                                # print('TypeOfSend?')
                                                # TypeOfSend = int(input())

                                                Message = ""
                                                for i in values['input']:
                                                    Message += i

                                                TypeOfSend = 1
                                                Type = numpy.int64(TypeOfSend)
                                                if TypeOfSend == 1:
                                                    # print('Enter message')

                                                    TextToSend = Message.encode(MYFORMAT)
                                                    NumpyInt = numpy.int64(len(TextToSend))
                                                    client.send(Type.tobytes())
                                                    client.send(NumpyInt.tobytes())
                                                    client.send(TextToSend)
                                                    window['chat'].Widget.yview_moveto(1.0)
                                                    break

                                                if TypeOfSend == 2:
                                                    # print('Enter path to file')
                                                    MyPath = input()
                                                    if os.path.isfile(MyPath):
                                                        client.send(Type.tobytes())
                                                        FileName = os.path.basename(MyPath)
                                                        sendFile(client, MyPath, FileName)
                                                    # else:
                                                    # print('Something is wrong and you know it')
                                                if TypeOfSend == 3:
                                                    # print('Enter message')
                                                    TextToSend = input().encode(MYFORMAT)
                                                    NumpyInt = numpy.int64(len(TextToSend))
                                                    # print('Enter path to file')
                                                    MyPath = input()
                                                    if os.path.isfile(MyPath):
                                                        client.send(Type.tobytes())
                                                        client.send(NumpyInt.tobytes())
                                                        client.send(TextToSend)
                                                        FileName = os.path.basename(MyPath)
                                                        sendFile(client, MyPath, FileName)

                                                #     else:
                                                #         print('Something is wrong and you know it')
                                                # print("Беседа и все ее сообщения")
                                                # print(AllConversations, sep="\n")
                                                # print("Беседа и user данные ее участников", sep="\n")
                                                # print(AllConversationsUsers)

                                    if event == 'Return':
                                        window.close()
                                        save_keys = []
                                        save_data = []

                                        MessengerWindow.clear()

                                        for i, j in AllConversations.items():
                                            nick = ""
                                            if i[1] == "default":
                                                for n in AllConversationsUsers[i]:
                                                    if n[0] != MyId:
                                                        nick = n[2]
                                                        break

                                                save_keys.append(str(i))
                                                create_key = []
                                                for k in range(3):
                                                    save_data.append(str(str(i) + str(k)))
                                                    create_key.append(str(str(i) + str(k)))
                                                if len(j) == 0:
                                                    MessengerWindow.append([sg.Frame(nick,
                                                                                     [[
                                                                                         sg.Input(str(i),
                                                                                                  key='SaveData',
                                                                                                  disabled=True,
                                                                                                  visible=False),
                                                                                         sg.Text('', enable_events=True,
                                                                                                 key=create_key[0],
                                                                                                 size=(5, 2)),
                                                                                         sg.Text('', enable_events=True,
                                                                                                 key=create_key[1],
                                                                                                 size=(16, 2)),
                                                                                         sg.Text('',
                                                                                                 enable_events=True,
                                                                                                 key=create_key[2],
                                                                                                 size=(8, 2))
                                                                                     ]], border_width=3,
                                                                                     font=('Times New Roman', 14))
                                                                            ])
                                                else:
                                                    MessengerWindow.append([sg.Frame(nick,
                                                                                     [[
                                                                                         sg.Input(str(i),
                                                                                                  key='SaveData',
                                                                                                  disabled=True,
                                                                                                  visible=False),
                                                                                         sg.Text(j[0][1],
                                                                                                 enable_events=True,
                                                                                                 key=create_key[0],
                                                                                                 size=(5, 2)),
                                                                                         sg.Text(j[0][3],
                                                                                                 enable_events=True,
                                                                                                 key=create_key[1],
                                                                                                 size=(16, 2)),
                                                                                         sg.Text(
                                                                                             str(((j[0][4].split(".")[
                                                                                                 0].split(
                                                                                                 ' '))[::-1])[
                                                                                                     0]) + "\n" + str(
                                                                                                 ((j[0][
                                                                                                       4].split(
                                                                                                     ".")[0].split(
                                                                                                     ' '))[::-1])[
                                                                                                     1]),
                                                                                             enable_events=True,
                                                                                             key=create_key[2],
                                                                                             size=(8, 2))
                                                                                     ]], border_width=3,
                                                                                     font=('Times New Roman', 14))
                                                                            ])

                                            else:
                                                save_keys.append(str(i))
                                                create_key = []
                                                for k in range(3):
                                                    save_data.append(str(str(i) + str(k)))
                                                    create_key.append(str(str(i) + str(k)))

                                                if len(j) == 0:
                                                    MessengerWindow.append([sg.Frame(str(i[1]),
                                                                                     [[
                                                                                         sg.Input(str(i),
                                                                                                  key='SaveData',
                                                                                                  disabled=True,
                                                                                                  visible=False),
                                                                                         sg.Text('', enable_events=True,
                                                                                                 key=create_key[0],
                                                                                                 size=(5, 2)),
                                                                                         sg.Text('', enable_events=True,
                                                                                                 key=create_key[1],
                                                                                                 size=(16, 2)),
                                                                                         sg.Text('',
                                                                                                 enable_events=True,
                                                                                                 key=create_key[2],
                                                                                                 size=(8, 2))
                                                                                     ]], border_width=3,
                                                                                     font=('Times New Roman', 14))
                                                                            ])
                                                else:
                                                    MessengerWindow.append([sg.Frame(str(i[1]),
                                                                                     [[
                                                                                         sg.Input(str(i),
                                                                                                  key='SaveData',
                                                                                                  disabled=True,
                                                                                                  visible=False),
                                                                                         sg.Text(j[0][1],
                                                                                                 enable_events=True,
                                                                                                 key=create_key[0],
                                                                                                 size=(5, 2)),
                                                                                         sg.Text(j[0][3],
                                                                                                 enable_events=True,
                                                                                                 key=create_key[1],
                                                                                                 size=(16, 2)),
                                                                                         sg.Text(
                                                                                             str(((j[0][4].split(".")[
                                                                                                 0].split(
                                                                                                 ' '))[::-1])[
                                                                                                     0]) + "\n" + str(
                                                                                                 ((j[0][
                                                                                                       4].split(
                                                                                                     ".")[0].split(
                                                                                                     ' '))[::-1])[
                                                                                                     1]),
                                                                                             enable_events=True,
                                                                                             key=create_key[2],
                                                                                             size=(8, 2))
                                                                                     ]], border_width=3,
                                                                                     font=('Times New Roman', 14))
                                                                            ])

                                        MessengerWindow = [[sg.Frame('Messages', [[sg.Column(MessengerWindow,
                                                                                             scrollable=True,
                                                                                             size=(300, 200),
                                                                                             vertical_scroll_only=True)]],
                                                                     border_width=5, font=('Times New Roman', 24))]]
                                        MessengerWindow.append([sg.Button('Write a new message'), sg.Button('Exit')])
                                        window = sg.Window('Chat', MessengerWindow, finalize=True)
                                        break

                else:
                    # print('Could not log in')
                    # window.close()
                    # break
                    popupBoi('There is no such user or password is wrong', title='Notification', keep_on_top=True, margins=(50, 10),
                             disable_close=False, element_justification='c')
                    continue
