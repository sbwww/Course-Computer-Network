import json
import socket
import sys
import threading
import tkinter
import tkinter.messagebox
from tkinter.scrolledtext import ScrolledText

from Parameters.ClientParams import *
from tkinter import messagebox


class Login_UI():
    def __init__(self, main_window):
        # region UI
        self.main_window = main_window

        self.main_window.title('登录')
        self.main_window.geometry('260x150+500+200')
        self.main_window.resizable(0, 0)

        default_ip = tkinter.StringVar()
        default_ip.set(SERVER_IP+':'+SERVER_PORT)
        default_username = tkinter.StringVar()
        default_username.set(USERNAME)

        # 服务器标签
        ip_label = tkinter.Label(self.main_window, text='服务器 IP')
        ip_label.place(x=20, y=20, width=80, height=20)

        self.ip_entry = tkinter.Entry(
            self.main_window, width=80, textvariable=default_ip)
        self.ip_entry.place(x=110, y=20, width=130, height=20)

        # 用户名标签
        labelUser = tkinter.Label(self.main_window, text='用户名')
        labelUser.place(x=20, y=60, width=80, height=20)

        self.username_entry = tkinter.Entry(
            self.main_window, width=80, textvariable=default_username)
        self.username_entry.place(x=110, y=60, width=130, height=20)

        # 登录按钮
        login_button = tkinter.Button(
            self.main_window, text='登录', command=self.login)
        login_button.place(x=100, y=100, width=60, height=30)
        # 回车绑定登录功能
        self.main_window.bind('<Return>', self.login)
        # endregion

    # 登录按钮事件
    def login(self, *args):
        global SERVER_IP, SERVER_PORT, USERNAME
        SERVER_IP, SERVER_PORT = self.ip_entry.get().split(':')  # 获取IP和端口号
        SERVER_PORT = int(SERVER_PORT)  # 端口号需要为int类型
        USERNAME = self.username_entry.get()
        self.main_window.destroy()  # 关闭窗口


class Chat_UI():
    def __init__(self, main_window):
        # region UI
        global USERNAME
        self.online_users_listbox = ''  # 用于显示在线用户的列表框
        self.online_users = []  # 在线用户列表
        self.chatter = '群聊'  # 聊天对象, 默认为群聊

        self.main_window = main_window
        self.main_window.geometry('590x420+320+100')
        self.main_window.resizable(0, 0)

        # 消息区域
        self.message_aera = ScrolledText(self.main_window)
        self.message_aera.place(x=5, y=5, width=450, height=360)
        # 消息区字体颜色
        self.message_aera.tag_config('red', foreground='red')
        self.message_aera.tag_config('blue', foreground='blue')
        self.message_aera.tag_config('green', foreground='green')
        self.message_aera.insert(tkinter.END, '您已进入聊天室\n', 'blue')

        # 在线用户区
        self.online_users_listbox = tkinter.Listbox(self.main_window)
        self.online_users_listbox.place(x=455, y=5, width=130, height=360)
        # 在用户列表绑定选择聊天对象事件
        self.online_users_listbox.bind(
            '<ButtonRelease-1>', self.select_chatter)

        # 消息编辑区
        self.message_text = tkinter.StringVar()
        self.message_text.set('')
        self.message_entry = tkinter.Entry(
            self.main_window, width=120, textvariable=self.message_text)
        self.message_entry.place(x=5, y=375, width=435, height=30)

        # 发送按钮
        self.send_button = tkinter.Button(
            self.main_window, text='发送', command=self.send)
        self.send_button.place(x=455, y=375, width=60, height=30)
        # 绑定回车发送信息
        self.main_window.bind('<Return>', self.send)

        # 清空按钮
        self.send_button = tkinter.Button(
            self.main_window, text='清空', command=self.clear)
        self.send_button.place(x=525, y=375, width=60, height=30)
        # endregion

        self.my_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.my_socket.connect((SERVER_IP, SERVER_PORT))

        # 用户名+=ip+port
        addr = self.my_socket.getsockname()  # 获取客户端ip和端口号
        addr = addr[0] + ':' + str(addr[1])  # SERVER_IP:port
        USERNAME = USERNAME + ' (' + addr + ')'
        self.main_window.title(USERNAME + ' 群聊')

        self.my_socket.send(USERNAME.encode())

        r = threading.Thread(target=self.recv)
        r.start()  # 开始线程接收信息

    # 清空按钮事件
    def clear(self, *args):
        self.message_text.set('')

    # 发送按钮事件
    def send(self, *args):
        self.online_users.append('群聊')
        if self.chatter not in self.online_users:
            tkinter.messagebox.showerror('发送失败', message='请选择聊天对象')
            return False
        if self.chatter == USERNAME:
            tkinter.messagebox.showerror('发送失败', message='请不要选择自己')
            return False
        msg = USERNAME + ':;' + self.message_entry.get() + ':;' + self.chatter
        self.my_socket.send(msg.encode())
        self.clear()  # 发送后清空文本框
        return True

    # 选择聊天对象事件
    def select_chatter(self, *args):
        # 获取点击的索引然后得到内容(用户名)
        index = self.online_users_listbox.curselection()[0]
        if index == 0 or index == 1:
            self.main_window.title(USERNAME + ' 群聊')
            self.chatter = '群聊'
        else:
            self.chatter = self.online_users_listbox.get(index)
            self.main_window.title(USERNAME + '  -->  ' + self.chatter)

    # 刷新在线列表
    def refresh_list(self, receive_data):
        self.online_users_listbox.delete(0, tkinter.END)  # 清空列表框
        online_count = ('在线人数: ' + str(len(receive_data)) + ' 人')
        self.online_users_listbox.insert(tkinter.END, online_count)
        self.online_users_listbox.itemconfig(
            tkinter.END, fg='black', bg="lightgray")
        self.online_users_listbox.insert(tkinter.END, '群聊')
        self.online_users_listbox.itemconfig(tkinter.END, fg='black')
        for data in receive_data:
            self.online_users_listbox.insert(
                tkinter.END, data)
            self.online_users_listbox.itemconfig(
                tkinter.END, fg='black')

    # 接收服务端发送的信息
    def recv(self):
        while True:
            receive_data = self.my_socket.recv(1024)
            receive_data = receive_data.decode()
            try:
                # 接收到在线用户列表
                receive_data = json.loads(receive_data)
                self.online_users = receive_data
                self.refresh_list(receive_data)
            except:
                # 接收到消息
                receive_data = receive_data.split(':;')
                data1 = receive_data[0]  # 发送信息的用户名
                data2 = receive_data[1].strip()  # 消息
                data3 = receive_data[2]  # 聊天对象
                if data3 == '群聊':
                    data2 = data1 + ' to all : ' + data2+'\n'
                    if data1 == USERNAME:  # 自己发送的
                        self.message_aera.insert(tkinter.END, data2, 'blue')
                    else:  # 接收的
                        self.message_aera.insert(
                            tkinter.END, data2, 'green')
                elif data1 == USERNAME or data3 == USERNAME:  # 私聊
                    data2 = data1 + ' to '+data3+' : ' + data2+'\n'
                    self.message_aera.insert(
                        tkinter.END, data2, 'red')
                self.message_aera.see(tkinter.END)

    def __del__(self):
        self.my_socket.close()  # 关闭 TCP 连接


if __name__ == '__main__':
    login_window = tkinter.Tk()
    login_ui = Login_UI(login_window)
    login_window.mainloop()

    print(USERNAME)

    chat_window = tkinter.Tk()
    chat_ui = Chat_UI(chat_window)
    chat_window.mainloop()
    chat_ui.__del__()
