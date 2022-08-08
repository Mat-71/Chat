import socket
import json
import time
import select
from key_generator import get_key_from_password
from encryption import *
from User import User
from conversion import to_bytes, from_bytes

"""
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server_socket.bind((IP, PORT))
server_socket.listen()
sockets_list = [server_socket]
users = {}
client = {}
client2 = {}
client3 = {}
f = 0
key = get_key_from_password('5', 8)
print(f'Listening for connections on {IP}: {PORT}...')

class Server:
    def __init__(self, ip: str, port: int, password: str, key_size: int):
        self.IP = "localhost"
        self.PORT = 42690
        self.HEADER_LENGTH = 10
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server_socket.bind((self.IP, self.PORT))
        self.server_socket.listen()
        self.sockets_list = [self.server_socket]
        self.users = {}
        self.clients = {}
        """
        example:
        self.users = {"username": User(username="username", pub_key=pub_key)}
        self.clients = {socket: {"username": username, "aes_key": aes_key, "checksum": checksum, "pub_key": pub_key}}
        """
        self.pub_key, self.priv_key = get_key_from_password(password, key_size)
        self.file_number = 0
        self.load()

    def load(self):
        users = None
        for user in range(3):
            try:
                with open(f"user{user}.json") as jsonFile:
                    users_2 = json.load(jsonFile)
                    jsonFile.close()
                if users is None:
                    users = users_2
                else:
                    if users[0] < users_2[0]:
                        users = users_2
                        self.file_number = (user + 1) % 3
            except IOError:
                pass
        self.users = {}
        if users is not None:
            users = users[1]
            for user in users:
                self.users[user['username']] = User(**user)

    def save(self):
        file_name = f"user{str(self.file_number)}.json"
        self.file_number = (self.file_number + 1) % 3
        with open(file_name, 'w') as outfile:
            outfile.write(json.dumps([int(time.time() * 1000), [u.__dict__() for u in self.users.values()]], indent=2))

    def receive_message(self, client_socket, target_type: type = str):
        try:
            message_header = client_socket.recv(self.HEADER_LENGTH)
            if not len(message_header):
                return False
            message_length = from_bytes(message_header, int)
            return from_bytes(client_socket.recv(message_length), target_type)
        except:
            return False

    def header(self, message):
        return b'\x00' * (self.HEADER_LENGTH - len(message)) + message

    def send(self, _message, _client):
        _message = to_bytes(_message)
        _client.send(self.header(_message) + _message)

    def aes_protocol(self, client_socket, username):
        pass

    def listen_client(self, notified_socket, m):
        if m is False:
            self.sockets_list.remove(notified_socket)
            return
        if m == 'key':  # send key to client
            self.send(self.pub_key, notified_socket)
            return
        if m[:3] == "aes" and len(m) == 3:  # server send aes key to client
            m = m.split('|')
            password = random_number(80)
            self.send(rsa.crypt(password, rsa.crypt(int(m[1]), self.priv_key)), notified_socket)
            password = to_bytes(f"{rsa.crypt(int(m[2]), self.priv_key)}{password}")
            self.clients[notified_socket] = {"password": password}
            return
        if notified_socket in self.clients:  # connection is secure
            password = self.clients[notified_socket][0]
            m = aes.decrypt(m, password).split("|")
            if len(client[notified_socket]) > 1:
                user = users[client[notified_socket][1]]
            else:
                user = False
            match m[0]:
                case 'login':
                    while len(m) > 2:
                        m[1] = m[1] + "|" + m[2]
                        del m[2]
                    username = m[1]
                    if username not in users:
                        send("1", notified_socket)
                        break
                    _check = str(random_number(80))
                    client1[notified_socket] = [_check, username, users[username]]
                    send(aes.encrypt(_check, password), notified_socket)
                case 'newlogin':
                    user_key = int(m[1])
                    while len(m) > 3:
                        m[2] = m[2] + "|" + m[3]
                        del m[3]
                    if m[2] not in users:
                        client2[notified_socket] = [m[2], user_key]
                        send(encrypt(username, key[1]), notified_socket)

                    else:
                        send("-1", notified_socket)
                case 'check':
                    if notified_socket not in client:
                        continue
                    user_key = users[client[notified_socket][1]].get_key()
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
                        users[client2[notified_socket][0]] = User(client2[notified_socket][0],
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
                        if m[1] in users and m[1] != user.get_username():
                            users[m[1]].add_request(user.get_username())
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
                        if m[1] in user.get_request() and m[1] != user.get_username():
                            user.add_friend(m[1])
                            users[m[1]].add_friend(user.get_username())
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
                            a = users[m[1]].get_key()
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
                            users[m[1]].new_message(m[2], user.get_username())
                            date = str(users[m[1]].get_message()[-1].get_date())

                            send(date, notified_socket)
                        else:
                            send("1", notified_socket)
                    else:
                        send("-1", notified_socket)
                case _:
                    print("erreur commande")
        else:
            print("connexion non securise")

    def listen(self):
        read_sockets, _, exception_sockets = select.select(self.sockets_list, [], self.sockets_list)
        for notified_socket in read_sockets:
            if notified_socket == self.server_socket:
                self.sockets_list.append(self.server_socket.accept()[0])
            else:
                self.listen_client(notified_socket, self.receive_message(notified_socket))
        for notified_socket in exception_sockets:
            self.sockets_list.remove(notified_socket)
            if notified_socket in self.clients:
                del self.clients[notified_socket]


if __name__ == "__main__":
    try:
        with open("user0.json") as jsonFile:
            user0 = json.load(jsonFile)
            jsonFile.close()
            f = 1
    except IOError:
        user0 = None
    try:
        with open("user1.json") as jsonFile:
            user1 = json.load(jsonFile)
            jsonFile.close()
            if user0 is None:
                user0 = user1
            else:
                if user0[0] < user1[0]:
                    user0 = user1
                    f = 2
    except IOError:
        pass
    try:
        with open("user2.json") as jsonFile:
            user1 = json.load(jsonFile)
            jsonFile.close()
            if user0 is None:
                user0 = user1
            else:
                if user0[0] < user1[0]:
                    user0 = user1
                    f = 0
    except IOError:
        pass
    if user0 is None:
        _user = {}
    else:
        user0 = user0[1]
        for i in user0:
            m = []
            for j in i['message']:
                m.append(Message(j['id'], j['username'], j['message'],
                                 datetime.datetime.strptime(j['date'], '%Y-%m-%d %H:%M:%S')))
            _user[i['username']] = User(i['username'], i['key'], i['id'], m, i['friend'], i['request'], i['pending'])
    del user0

    while True:
        file_name = 'user' + str(f) + '.json'
        f += 1
        f %= 3
        print(file_name)
        with open(file_name, 'w') as outfile:
            outfile.write(json.dumps([time.time(), [u.__dict__() for u in _user.values()]], indent=4))
            outfile.close()
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
                            if m[1] in user.get_request() and m[1] != user.get_username():
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
