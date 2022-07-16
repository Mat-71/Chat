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


class user:
    def __init__(self, username, friend=None, request=None, pending=None):
        if pending is None:
            pending = []
        if request is None:
            request = []
        if friend is None:
            friend = []
        self.username = username
        self.friend = friend
        self.request = request
        self.pending = pending

    def get_username(self):
        return self.username

    def get_friend(self):
        return self.friend

    def get_request(self):
        return self.request

    def get_pending(self):
        return self.pending

    def add_friend(self, friend):
        self.friend.append(friend)

    def add_request(self, request):
        self.request.append(request)

    def add_pending(self, pending):
        self.pending.append(pending)


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
            match m[0]:
                case 'login':
                    user = m[1]
                    if user not in _user:
                        send("-1", notified_socket)
                        break
                    _check = str(random.Random().randint(0, 100000))
                    client[notified_socket] = [_check, user]
                    check = encrypt(_check, _user[user][0])
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
                    user_key = _user[client[notified_socket][1]][0]
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
                        _user[client2[notified_socket][0]] = [client2[notified_socket][1], [], [], []]
                        print('Accepted new connection from {}'.format(client2[notified_socket][0]))
                        client3[notified_socket] = client2[notified_socket][0]
                    del client2[notified_socket]
                case 'getfriend':
                    if notified_socket in client3:
                        send(encrypt(_user[client3[notified_socket]][1], _user[client3[notified_socket]][0]),
                             notified_socket)
                    else:
                        send("-1", notified_socket)
                case 'newfriend':
                    if notified_socket in client3:
                        if m[1] in _user:
                            _user[m[1]][3].append(client3[notified_socket])
                            _user[client3[notified_socket]][2].append(m[1])
                            send('0', notified_socket)
                        else:
                            send('1', notified_socket)
                    else:
                        send("-1", notified_socket)
                case 'getfriendaccept':
                    if notified_socket in client3:
                        send(encrypt(_user[client3[notified_socket]][3], _user[client3[notified_socket]][0]),
                             notified_socket)
                    else:
                        send("-1", notified_socket)
                case 'friendaccept':
                    if notified_socket in client3:
                        if m[1] in _user[client3[notified_socket]][3]:
                            _user[client3[notified_socket]][1].append(m[1])
                            _user[client3[notified_socket]][3].remove(m[1])
                            _user[m[1]][1].append(client3[notified_socket])
                            _user[m[1]][2].remove(client3[notified_socket])
                            send("0", notified_socket)
                        else:
                            send("1", notified_socket)
                    else:
                        send("-1", notified_socket)
                case 'friendpending':
                    if notified_socket in client3:
                        send(encrypt(_user[client3[notified_socket]][2], _user[client3[notified_socket]][0]),
                             notified_socket)
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
