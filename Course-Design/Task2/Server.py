import socket
import threading
import queue
import json

from Parameters.ServerParams import *


class TCP_Server():
    def __init__(self):
        self.que = queue.Queue()  # 客户端发送信息队列
        self.users = []  # 在线用户信息  [conn, username, addr]
        self.lock = threading.Lock()  # 创建锁, 防止多个线程写入数据的顺序打乱

        self.my_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.my_socket.bind((IP, PORT))
        self.my_socket.listen(5)
        print('tcp server online...')

    # 接收客户端发送信息
    def tcp_connect(self, conn, addr):
        username = conn.recv(1024)
        username = username.decode()
        self.users.append((conn, username, addr))
        print('新连接:', addr, ':', username)
        online_list = self.onlines()
        self.recv(addr, online_list)
        try:
            while True:
                data = conn.recv(1024)
                data = data.decode()
                self.recv(addr, data)  # 保存信息到队列
            conn.close()
        except:
            print(username + ' 断开连接')
            self.delUsers(conn, addr)  # 移除断开用户
            conn.close()

    # 判断断开用户在users中是第几位并移出列表, 刷新客户端的在线用户显示
    def delUsers(self, conn, addr):
        a = 0
        for user in self.users:
            if user[0] == conn:
                self.users.pop(a)
                print('剩余在线用户: ')
                online_list = self.onlines()
                self.recv(addr, online_list)
                print(online_list)
                break
            a += 1

    # 将接收到的信息存入队列
    def recv(self, addr, data):
        self.lock.acquire()
        try:
            self.que.put((addr, data))
        finally:
            self.lock.release()

    # 将队列que中的消息发送给所有连接到的用户
    def sendData(self):
        while True:
            if not self.que.empty():
                data = ''
                message = self.que.get()  # 取出队列第一个元素
                if isinstance(message[1], str):  # 如果data是str则返回Ture
                    for i in range(len(self.users)):
                        # username[i][1]是用户名, self.users[i][2]是addr, 将message[0]改为用户名
                        for j in range(len(self.users)):
                            if message[0] == self.users[j][2]:
                                data = message[1]
                                break
                        self.users[i][0].send(data.encode())
                data = data.split(':;')[0]
                if isinstance(message[1], list):  # 同上
                    data = json.dumps(message[1])
                    for i in range(len(self.users)):
                        self.users[i][0].send(data.encode())

    # 将在线用户存入online列表并返回
    def onlines(self):
        online = []
        for user in self.users:
            online.append(user[1])
        return online

    def __del__(self):
        self.my_socket.close()


if __name__ == '__main__':
    server = TCP_Server()
    q = threading.Thread(target=server.sendData)
    q.start()
    while True:
        conn, addr = server.my_socket.accept()
        t = threading.Thread(target=server.tcp_connect, args=(conn, addr))
        t.start()
