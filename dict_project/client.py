

from socket import *
import sys
import os

HOST = '127.0.0.1'
PORT = 8889
ADDR = (HOST, PORT)


def menu1():
    print('========欢迎来到英英字典========')
    print('| 1.注册     2.登录     3.退出 |')


def menu2():
    print('========欢迎使用英英词典=========')
    print('| 1.查词   2.查询历史记录  3.注销 |')


def register(sk):
    while True:
        name = input("请输入注册名称：")
        if not name:
            print("用户名不能为空")
            continue
        msg = 'R ' + name
        sk.send(msg.encode())
        data = sk.recv(1024).decode()
        if data == "OK":
            while True:
                code = input("请输入6-18位的密码：")
                if len(code) > 6 and len(code) < 18:
                    sk.send(code.encode())
                    msg = sk.recv(1024).decode()
                    if msg == "OK":
                        print("注册成功，请重新登录！")
                        break
                    else:
                        print('注册失败')
                        continue
                else:
                    print("密码格式错误，请重新输入！")
                    continue
        else:
            print("用户名已存在，请重新注册！")
            continue
        break


def do_search(sk, name):
    msg = "S"
    sk.send(msg.encode())
    while True:
        word = input("请输入单词(输入‘退出’退出)：")
        if word == '退出':
            msg1 = name + ' ' + word
            sk.send(msg1.encode())
            break
        if not word:
            print("请输入单词")
            continue
        msg = name + ' ' + word
        sk.send(msg.encode())
        data = sk.recv(1024).decode()
        if data == "OK":
            sk.send(b'OK')
            print(sk.recv(1024).decode())
            continue
        if data == "FALL":
            print("没有这个单词")
            continue


def do_history(sk, name):
    while True:
        msg = 'H ' + name
        sk.send(msg.encode())
        while True:
            data = sk.recv(1024).decode()
            if data == "FALL":
                print("记录为空")
                break
            elif data == "OK":
                break
            else:
                print(data)
        while True:
            msg1 = input("输入1退出，输入2再次查询：")
            if msg1 == '1':
                return
            elif msg1 == '2':
                break
            else:
                print("输入错误！")
                continue


def do_login(sk):
    while True:
        name = input("请输入用户名：")
        if not name:
            print("用户名不为空")
            continue
        msg = 'L ' + name
        sk.send(msg.encode())
        data = sk.recv(1024).decode()
        if data == "OK":
            while True:
                code = input("请输入密码：")
                sk.send(code.encode())
                msg = sk.recv(1024).decode()
                if msg == "OK":
                    print("登录成功！")
                    while True:
                        menu2()
                        ctl = input("请选择功能：")
                        if ctl == '1' or ctl == '查词':
                            do_search(sk, name)
                            continue
                        elif ctl == '2' or ctl == '查询历史记录':
                            do_history(sk, name)
                        elif ctl == '3' or ctl == '退出':
                            return

                else:
                    print("密码错误，请重新输入")
                    continue
        else:
            print("用户名不存在！请重新输入")
            continue


def do_quit(sk):
    msg = 'Q'
    sk.send(msg.encode())
    print("退出成功")


def main():
    sk = socket()
    try:
        sk.connect(ADDR)
    except Exception:
        sk.close()
        sys.exit(1)
    while True:
        menu1()
        text = input("请选择功能：")
        if text == '1' or text == '注册':
            register(sk)
            continue
        elif text == '2' or text == '登录':
            do_login(sk)
            continue
        elif text == '3' or text == '退出':
            do_quit(sk)
            sys.exit(0)
        else:
            print("没有此功能！")
            continue


if __name__ == '__main__':
    main()
