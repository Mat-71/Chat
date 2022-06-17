from rsa import *
import socket
import sys
import errno
from key_generator import get_key_from_password
sys.setrecursionlimit(15000)
HEADER_LENGTH = 10
IP = "localhost"
PORT = 42690
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect((IP, PORT))
client_socket.setblocking(False)


def receive():
    try:
        header = client_socket.recv(HEADER_LENGTH)
        if not len(header):
            print('Connection closed by the server')
            sys.exit()
        header = int(header.decode('utf-8').strip())
        m = client_socket.recv(header).decode('utf-8')
        return m
    except IOError as e:
        if e.errno != errno.EAGAIN and e.errno != errno.EWOULDBLOCK:
            print('Reading error: {}'.format(str(e)))
            sys.exit()
    except Exception as e:
        print('Reading error: '.format(str(e)))
        sys.exit()
    return False


def send(message):
    header = f"{len(message):<{HEADER_LENGTH}}".encode('utf-8')
    client_socket.send(header + message.encode('utf-8'))


def login(user: str):
    user = code('login|' + user, s_key, 0).encode('utf-8')
    send(user)
    check = receive()
    if check == "-1":
        return 1
    check = code('check|' + code(check, key[1], 1), s_key, 0)
    send(check)
    return receive()


def new_login(user: str):
    send(code('newlogin|' + str(key[0][0]) + "," + str(key[0][1]) + "|" + user, s_key, 0))
    a = receive()
    if a == '-1':
        return 1
    a = code(a, key[1], 1)
    if a == user:
        send("0")
    else:
        send("-1")


username = input()
password = input()
key = get_key_from_password(username+password)
send("key")
while True:
    s_key = receive()
    if s_key is not False:
        break
s_key = (int(s_key[0]), int(s_key[1]))
new_login(username)

"""
a = code(username, key[0], 0)
print(a)
print(code(a, key[1], 1))
while True:
    message = input(f'{my_username} > ')
    if message:
        message = message.encode('utf-8')
        message_header = f"{len(message):<{HEADER_LENGTH}}".encode('utf-8')
        client_socket.send(message_header + message)

    try:
        while True:
            username_header = client_socket.recv(HEADER_LENGTH)
            if not len(username_header):
                print('Connection closed by the server')
                sys.exit()
            username_length = int(username_header.decode('utf-8').strip())
            username = client_socket.recv(username_length).decode('utf-8')
            message_header = client_socket.recv(HEADER_LENGTH)
            message_length = int(message_header.decode('utf-8').strip())
            message = client_socket.recv(message_length).decode('utf-8')
            print(f'{username} > {message}')
    except IOError as e:
        if e.errno != errno.EAGAIN and e.errno != errno.EWOULDBLOCK:
            print('Reading error: {}'.format(str(e)))
            sys.exit()
        continue
    except Exception as e:
        print('Reading error: '.format(str(e)))
        sys.exit()
"""
