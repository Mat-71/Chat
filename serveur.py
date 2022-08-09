import socket
import json
import time
import select
from key_generator import get_key_from_password, random_number
import rsa
import aes
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
client1 = {}
f = 0
pub_key, priv_key = get_key_from_password('5', 8)"""


class Server:
    def __init__(self, ip: str, port: int, password: str, key_size: int):
        self.IP = ip
        self.PORT = port
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
        self.clients = {socket: {"username": username, "aes_key": aes_key, "check": check, "pub_key": pub_key, "auth": auth}}
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
        except Exception as e:
            print(e)
            return False

    def header(self, message: bytes) -> bytes:
        return b'\x00' * (self.HEADER_LENGTH - len(message)) + message

    def send(self, _message, _client):
        _message = to_bytes(_message)
        _client.send(self.header(_message) + _message)

    def send_public_key(self, client_socket: socket.socket):
        self.send(self.pub_key, client_socket)

    def aes_protocol(self, client_socket: socket.socket, data: str):
        data = data.split('|')
        if len(data) != 2:
            return
        server_random_number = random_number(80)
        self.send(rsa.crypt(server_random_number, rsa.crypt(int(data[0]), self.priv_key)), client_socket)
        client_random_number = rsa.crypt(int(data[2]), self.priv_key)
        aes_key = client_random_number.to_bytes(10, 'big') + server_random_number.to_bytes(10, 'big')
        self.clients[client_socket] = {"aes_key": aes_key, "auth": False}

    def login(self, client_data: dict, aes_key: bytes, client_socket: socket.socket, username: str):
        if username not in self.users:
            self.send("1", client_socket)
            return
        _check = random_number(2024)
        client_data['check'] = _check
        client_data['username'] = username
        key = self.users[username].pub_key
        self.send(aes.encrypt(str(rsa.crypt(_check, key)), aes_key), client_socket)

    def check_login(self, client_data: dict, client_socket: socket.socket, aes_key: bytes, check: int):
        if "check" not in client_data or "username" not in client_data:
            return
        if client_data["check"] != check:
            return self.send(aes.encrypt("1", aes_key), client_socket)
        self.send('0', client_socket)
        print('Accepted new connection from {}'.format(client_data["username"]))
        client_data["auth"] = True

    def sign_up(self, client_data: dict, aes_key: bytes, client_socket: socket.socket, data: str):
        user_key = data.split("|", 1)[0]
        username = data.removeprefix(user_key).removeprefix('|')
        user_key = int(user_key)
        if username in self.users or user_key <= 0 or len(username) <= 3:
            return self.send(aes.encrypt("1", aes_key), client_socket)
        client_data['username'] = username
        client_data['auth'] = True
        self.users[data[2]] = User(username, user_key)
        print('Accepted new connection from {}'.format(username))
        self.send(aes.encrypt("0", aes_key), client_socket)

    def friend_request(self, client_socket: socket.socket, user: User, friend_name: str):
        if friend_name not in self.users or friend_name == user.username:
            return self.send('1', client_socket)
        self.users[friend_name].add_request(user.username)
        user.add_pending(friend_name)
        self.send('0', client_socket)

    def accept_friend(self, client_socket: socket.socket, user: User, friend_name: str):
        if friend_name not in user.get_requests():
            return self.send("1", client_socket)
        user.add_friend(friend_name)
        self.users[friend_name].add_friend(user.username)
        self.send("0", client_socket)

    def get_friend_pub_key(self, client_socket: socket.socket, aes_key: bytes, user: User, friend_name: str):
        if friend_name not in user.friends:
            return self.send("1", client_socket)
        self.send(aes.encrypt(self.users[friend_name].pub_key, aes_key), client_socket)

    def aes_data_receive(self, client_socket, data):
        client_data = self.clients[client_socket]
        aes_key = client_data["aes_key"]
        data = aes.decrypt(data, aes_key)
        action = data.split("|", 1)[0]
        data = data.removeprefix(action).removeprefix('|')
        match action:
            case 'login':  # ex: "login|username"
                return self.login(client_data, client_socket, aes_key, data)
            case 'check login':  # ex: "check login|check"
                return self.check_login(client_data, client_socket, aes_key, int(data))
            case 'sign up':  # ex: "sign up|user_key|username"
                # TODO: check if user password is strong enough
                return self.sign_up(client_data, aes_key, client_socket, data)
        if "username" not in client_data or not client_data["auth"]:
            return self.send("-1", client_socket)
        user = self.users[client_data["username"]]
        match action:
            case 'get friends':  # ex: "get friends"
                return self.send(aes.encrypt(user.get_friends(), aes_key), client_socket)
            case 'friend request':  # ex: "friend request|username" TODO: send random number
                return self.friend_request(client_socket, user, data)
            case 'get requests':  # ex: "get requests"
                return self.send(aes.encrypt(user.get_requests(), aes_key), client_socket)
            case 'accept friend':  # ex: "accept friend|username" TODO: send random number
                return self.accept_friend(client_socket, user, data)
            case 'get pendings':  # ex: "get pendings"
                return self.send(aes.encrypt(user.get_pendings(), aes_key), client_socket)
            case 'get pub key':  # ex: "get friend pub key|username"
                return self.get_friend_pub_key(client_socket, aes_key, user, data)
            case 'get friend aes key':  # ex: "get friend aes key|username"
                friend_name = data
                if friend_name not in user.friends:
                    return self.send("1", client_socket)
                self.send(aes.encrypt(user.get_aes_key(friend_name), aes_key), client_socket)
            case 'message':  # ex: "message|content|username
                # ???
                content = data.split("|", 1)[0]
                username = data.removeprefix(action).removeprefix('|')
                if isinstance(user, User):
                    if username in user.friends:
                        self.users[username].new_message(content, user)
                        self.send(self.users[username].get_message()[-1].get_date(), client_socket)
                    else:
                        self.send("1", client_socket)
                else:
                    self.send("-1", client_socket)
            case _:
                print("erreur commande")

    def listen_client(self, client_socket: socket.socket, data: str | bool | bytes):
        if data is False:
            return self.sockets_list.remove(client_socket)
        if data == 'key':  # send key to client
            return self.send_public_key(client_socket)
        if data.startswith("aes"):  # server send aes key to client
            return self.aes_protocol(client_socket, data.removeprefix("aes").removeprefix('|'))
        if client_socket in self.clients and isinstance(data, bytes):  # connection is secure
            self.aes_data_receive(client_socket, data)
        else:
            print("connexion non securisée")

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
    server = Server("", 42690, "5", 8)
    print(f'Listening for connections on {server.IP}: {server.PORT}...')
    while True:
        server.listen()
        server.save()
