

from socket import *
import os
import sys
import pymysql
import signal
import time
DICT_TEXT = './dict.txt'
HOST = '127.0.0.1'
PORT = 8889
ADDR = (HOST, PORT)


def do_register(conn, cur, db, name):
    cur.execute("select name from name_code;")
    message = list(cur.fetchall())
    if len(message) < 1:
        conn.send(b"OK")
    else:
        while True:
            for i in message:
                for a in i:
                    print(a)
                    if a == name:
                        conn.send(b"FALL")
                        return
            conn.send(b"OK")
            break
    data = conn.recv(1024).decode()
    if not data:
        conn.send(b'FALL')
        return
    cur.execute("insert into name_code values('%s', '%s');" % (name, data))
    conn.send(b"OK")
    db.commit()


def do_login(conn, cur, db, name):
    cur.execute("select name from name_code;")
    message = list(cur.fetchall())
    if len(message) < 1:
        conn.send(b'FALL')
    else:
        while True:
            for i in message:
                for a in i:
                    if a == name:
                        print("jjjjj")
                        conn.send(b'OK')
                        cur.execute("select code from name_code where name='%s';" % name)
                        while True:
                            password = conn.recv(1024).decode()
                            for i in cur.fetchone():
                                if password == i:
                                    conn.send(b"OK")
                                    return
                                else:
                                    conn.send(b'FALL')
                                    continue
            conn.send(b'FALL')
            return


def do_history(sk, cur, db, name):
    cur.execute("select * from search_history where name='%s';" % name)
    message = list(cur.fetchall())
    if len(message) == 0:
        sk.send(b"FALL")
        return
    else:
        for i in message:
            LT = list(i)
            msg1 = '%s  %s  %s' % (LT[0], LT[1], LT[2])
            sk.send(msg1.encode())
            time.sleep(0.1)
        sk.send(b"OK")
        return


def do_search(conn, cur, db, data):
    while True:
        recv_msg = conn.recv(1024).decode()
        data = recv_msg.split(' ', 1)
        if data[1] == '退出':
            return
        with open(DICT_TEXT, 'r') as f:
            while True:
                read_message = f.readline()
                if read_message == '':
                    conn.send(b'FALL')
                    break
                msg = read_message.split(' ', 1)
                if msg[0] == data[1]:
                    conn.send(b'OK')
                    msg1 = conn.recv(1024).decode()
                    if msg1 == 'OK':
                        msg2 = read_message.strip('\n')
                        conn.send(msg2.encode())
                        time1 = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
                        cur.execute("select * from search_history\
                         where name='%s';" % data[0])
                        if len(cur.fetchall()) == 20:
                            cur.execute("delete from search_history\
                                where name='%s' limit 1;" % data[0])
                        cur.execute("insert into search_history values(\
                            '%s','%s','%s');" % (data[0], time1, data[1]))
                        db.commit()
                        break
                    else:
                        return


def do_child(conn):
    db = pymysql.connect("localhost", 'root', '123456', charset='utf8')
    cur = db.cursor()
    cur.execute("use dict;")
    while True:
        data = conn.recv(1024).decode()
        data = data.split(' ', 1)
        if data[0] == 'R':
            do_register(conn, cur, db, data[1])
        elif data[0] == 'L':
            do_login(conn, cur, db, data[1])
        elif data[0] == 'H':
            do_history(conn, cur, db, data[1])
        elif data[0] == 'S':
            do_search(conn, cur, db, data)
        elif data[0] == 'Q':
            conn.close()
            break
    cur.close()
    db.close()


def main():
    sk = socket()
    sk.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
    sk.bind(ADDR)
    sk.listen(10)
    signal.signal(signal.SIGCHLD, signal.SIG_IGN)
    while True:
        try:
            conn, addr = sk.accept()
        except KeyboardInterrupt:
            sk.close()
            sys.exit(0)
        except Exception:
            continue
        pid = os.fork()
        if pid < 0:
            print("创建子进程失败")
            continue
        elif pid == 0:
            sk.close()
            do_child(conn)
        else:
            conn.close()
            continue


if __name__ == "__main__":
    main()
