import random
import socket
import select
from key_generator import get_key_from_password
from encryption import *

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
client2 = {}
key = get_key_from_password('5', 8)
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


def send(message, a):
    message = message.encode('utf-8')
    header = f"{len(message):<{HEADER_LENGTH}}".encode('utf-8')
    a.send(header + message)


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
                send(private, notified_socket)
                continue
            m = decrypt(m, key[1]).split("|")
            print(m)
            if m[0] == 'login':
                user = m[1]
                print(m[1])
                if user not in _user:
                    send("-1", notified_socket)
                    break
                _check = str(random.Random().randint(0, 100000))
                client[notified_socket] = [_check, user]
                check = encrypt(_check, _user[user][0])
                send(check, notified_socket)
            elif m[0] == 'newlogin':
                print(m[1])
                user_key = m[1].split(',')
                user_key = (int(user_key[0]), int(user_key[1]))
                while len(m) > 3:
                    m[2] = m[2] + "|" + m[3]
                    del m[3]
                user = decrypt(m[2], user_key)
                if user not in _user:
                    client2[notified_socket] = [user, user_key]
                    send(encrypt(user, key[1]), notified_socket)

                else:
                    send("-1", notified_socket)
            elif m[0] == "check":
                user_key = _user[client[notified_socket][1]][0]
                if client[notified_socket][0] == decrypt(m[1], user_key):
                    send('0', notified_socket)
                else:
                    send('1', notified_socket)
                    print('Accepted new connection from {}'.format(client[notified_socket][1]))
            elif m[0] == "check2":
                if m[1] == "0":
                    _user[client2[notified_socket][0]] = [client2[notified_socket][1]]
                    print('Accepted new connection from {}'.format(client2[notified_socket][0]))
    for notified_socket in exception_sockets:
        sockets_list.remove(notified_socket)
