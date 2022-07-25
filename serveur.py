import datetime
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
client3 = {}
key = get_key_from_password('5', 8)
print(f'Listening for connections on {IP}: {PORT}...')


class User:
    def __init__(self, _username, _key, _id=0, _message=None, friend=None, request=None, pending=None):
        if pending is None:
            pending = []
        if request is None:
            request = []
        if friend is None:
            friend = []
        if _message is None:
            _message = []
        self.message = _message
        self.username = _username
        self.key = _key
        self.friend = friend
        self.request = request
        self.pending = pending
        self.id = _id

    def get_username(self):
        return self.username

    def get_key(self):
        return self.key

    def get_friend(self):
        return "|".join(self.friend)

    def get_request(self):
        return "|".join(self.request)

    def get_pending(self):
        return "|".join(self.pending)

    def add_friend(self, friend):
        self.friend.append(friend)
        if friend in self.request:
            self.request.remove(friend)
        if friend in self.pending:
            self.pending.remove(friend)

    def add_request(self, request):
        self.request.append(request)

    def add_pending(self, pending):
        self.pending.append(pending)

    def new_message(self, _message, _username):
        self.message.append(Message(self.id, _username, _message))
        self.id += 1

    def get_message(self):
        return self.message


class Message:
    def __init__(self, _id, _username: str, _message: str, date=datetime.datetime.now().replace(microsecond=0)):
        self.username = _username
        self.message = _message
        self.date = date
        self.id = _id

    def __str__(self):
        return f'{len(self.message)}|{self.id}|{self.date}|{self.username}|{self.message}'

    def __repr__(self):
        return f'{len(self.message)}|{self.id}|{self.date}|{self.username}|{self.message}'

    def get_date(self):
        return self.date


def receive_message(client_socket):
    try:
        message_header = client_socket.recv(HEADER_LENGTH)
        if not len(message_header):
            return False
        message_length = int(message_header.decode('utf-8').strip())
        return client_socket.recv(message_length).decode('utf-8')
    except:
        return False


def send(_message, a):
    _message = _message.encode('utf-8')
    header = f"{len(_message):<{HEADER_LENGTH}}".encode('utf-8')
    a.send(header + _message)

_user['admin'] = User('admin', get_key_from_password('admin')[0], friend=['a'])
_user['a'] = User('a', get_key_from_password('a')[0], friend=['admin'])
while True:
    read_sockets, _, exception_sockets = select.select(sockets_list, [], sockets_list)
    for notified_socket in read_sockets:
        if notified_socket == server_socket:
            sockets_list.append(server_socket.accept()[0])
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
            if notified_socket in client3:
                user = _user[client3[notified_socket]]
            else:
                user = False
            match m[0]:
                case 'login':
                    username = m[1]
                    if username not in _user:
                        send("-1", notified_socket)
                        break
                    _check = str(random.Random().randint(0, 10000000000000))
                    client[notified_socket] = [_check, username]
                    check = encrypt(_check, _user[username].get_key())
                    send(check, notified_socket)
                case 'newlogin':
                    user_key = m[1].split(',')
                    user_key = (int(user_key[0]), int(user_key[1]))
                    while len(m) > 3:
                        m[2] = m[2] + "|" + m[3]
                        del m[3]
                    username = decrypt(m[2], user_key)
                    if username not in _user:
                        client2[notified_socket] = [username, user_key]
                        send(encrypt(username, key[1]), notified_socket)

                    else:
                        send("-1", notified_socket)
                case 'check':
                    if notified_socket not in client:
                        continue
                    user_key = _user[client[notified_socket][1]].get_key()
                    if client[notified_socket][0] == decrypt(m[1], user_key):
                        send('0', notified_socket)
                    else:
                        send('1', notified_socket)
                        print('Accepted new connection from {}'.format(client[notified_socket][1]))
                        client3[notified_socket] = client[notified_socket][1]
                    del client[notified_socket]
                case 'check2':
                    if notified_socket not in client2:
                        continue
                    if m[1] == "0":
                        _user[client2[notified_socket][0]] = User(client2[notified_socket][0],
                                                                  client2[notified_socket][1])
                        print('Accepted new connection from {}'.format(client2[notified_socket][0]))
                        client3[notified_socket] = client2[notified_socket][0]
                    del client2[notified_socket]
                case 'getfriend':
                    if user:
                        send(encrypt(user.get_friend(), user.get_key()), notified_socket)
                    else:
                        send("-1", notified_socket)
                case 'friendrequest':
                    if user:
                        if m[1] in _user and m[1] != user.get_username():
                            _user[m[1]].add_request(user.get_username())
                            user.add_pending(m[1])
                            send('0', notified_socket)
                        else:
                            send('1', notified_socket)
                    else:
                        send("-1", notified_socket)
                case 'getrequest':
                    if user:
                        send(encrypt(user.get_request(), user.get_key()), notified_socket)
                    else:
                        send("-1", notified_socket)
                case 'friendaccept':
                    if user:
                        if m[1] in user.get_request()and m[1] != user.get_username():
                            user.add_friend(m[1])
                            _user[m[1]].add_friend(user.get_username())
                            send("0", notified_socket)
                        else:
                            send("1", notified_socket)
                    else:
                        send("-1", notified_socket)
                case 'getpending':
                    if user:
                        send(encrypt(user.get_pending(), user.get_key()), notified_socket)
                    else:
                        send("-1", notified_socket)
                case 'getfriendkey':
                    if user:
                        if m[1] in user.get_friend():
                            a = _user[m[1]].get_key()
                            a = str(a[0]) + "|" + str(a[1])
                            send(encrypt(a, user.get_key()), notified_socket)
                        else:
                            send("1", notified_socket)
                    else:
                        send("-1", notified_socket)
                case 'message':
                    while len(m) > 3:
                        m[2] = m[2] + "|" + m[3]
                        del m[3]
                    if user:
                        if m[1] in user.get_friend():
                            _user[m[1]].new_message(m[2], user.get_username())
                            date = str(_user[m[1]].get_message()[-1].get_date())

                            send(date, notified_socket)
                        else:
                            send("1", notified_socket)
                    else:
                        send("-1", notified_socket)
                case _:
                    print("erreur commande")
    for notified_socket in exception_sockets:
        sockets_list.remove(notified_socket)
        if notified_socket in client:
            del client[notified_socket]
        if notified_socket in client2:
            del client2[notified_socket]
        if notified_socket in client3:
            del client3[notified_socket]
