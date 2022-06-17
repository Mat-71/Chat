import random
import socket
import select
from key_generator import get_key_from_password
from rsa import *

HEADER_LENGTH = 10

IP = ''
PORT = 42690
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server_socket.bind((IP, PORT))
server_socket.listen()
sockets_list = [server_socket]
_user = {}
client = {}
key = get_key_from_password('2')
print(f'Listening for connections on {IP}: {PORT}...')


def receive_message(client_socket):
    try:
        message_header = client_socket.recv(HEADER_LENGTH)
        if not len(message_header):
            return False
        message_length = int(message_header.decode('utf-8').strip())
        return client_socket.recv(message_length).decode('utf-8')
    except:
        return False


def send(message):
    header = f"{len(message):<{HEADER_LENGTH}}".encode('utf-8')
    print(message)
    client_socket.send(header + message.encode('utf-8'))


while True:
    read_sockets, _, exception_sockets = select.select(sockets_list, [], sockets_list)
    for notified_socket in read_sockets:
        if notified_socket == server_socket:
            client_socket, client_address = server_socket.accept()
            sockets_list.append(client_socket)
        else:
            m = receive_message(notified_socket)
            if m is False:
                sockets_list.remove(notified_socket)
                continue
            if m == 'key':
                private = (str(key[0][0]) + "," + str(key[0][1]))
                send(private)
                continue
            m = code(m, key[0], 1).split("|")
            if m[0] == 'login':
                user = m[1]
                if user not in _user:
                    notified_socket.send(f"-1")
                    break
                _check = str(random.Random().random())
                client[notified_socket] = [_check, user]
                check = code(_check, _user[user][0], 0)
                send(check)
            elif m[0] == 'newlogin':
                user_key = m[1].split(',')
                user_key = (int(user_key[0]), int(user_key[1]))
                user = code(m[2], user_key, 1)
                if user not in _user:
                    if receive_message(notified_socket) == "0":
                        notified_socket.send(code(user, user_key, 0))
                        _user[user] = [user_key]
                else:
                    notified_socket.send(f"-1")
            elif m[0] == "check":
                user_key = _user[client[notified_socket][1]]
                if client[notified_socket][0] == code(m[1], user_key, 1):
                    send('0')
                else:
                    send('1')
                    print('Accepted new connection from {}'.format(client[notified_socket][1]))
    for notified_socket in exception_sockets:
        sockets_list.remove(notified_socket)
