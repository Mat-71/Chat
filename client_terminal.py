import datetime
import json
import time

import aes
import rsa
import socket
import sys
import errno
from key_generator import get_key_from_password, random_number
from conversion import to_bytes, from_bytes

sys.setrecursionlimit(15000)


class Client:
    def __init__(self, _username: str, pub_key: int, priv_key: tuple[int, int], new: bool = False):
        self.server_address = ("localhost", 42690)
        self.HEADER_LENGTH = 10
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.connect(self.server_address)
        self.server_socket.setblocking(False)
        self.username = _username
        self.pub_key = pub_key
        self.priv_key = priv_key
        self.messages = {}  # messages = {friend: [message, message, message]}
        self.keys = {}  # key = {"username": aes_key}
        self.requests = []  # requests = {"username": key}
        self.pendings = []  # pendings = {"username": key}
        self.is_connected = -1
        self.server_aes_key = None
        self.last_ping = time.time()
        self.aes_protocol()
        if self.server_aes_key is None:
            return
        self.is_connected = 0
        if not self.connexion(new):
            return
        self.is_connected = 1
        if new:
            self.load()
        self.ping_server()

    def load(self):
        # load messages, keys, requests, pendings from json file "[self.username].json" in the same directory
        try:
            with open(self.username + ".json", "r") as f:
                data = json.load(f)
                self.messages = data["messages"]
                self.keys = data["keys"]
                self.requests = data["requests"]
                self.pendings = data["pendings"]
        except FileNotFoundError:
            pass

    def start_transmission(self):
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.connect(self.server_address)
        self.server_socket.setblocking(False)

    def end_transmission(self):
        self.server_socket.close()

    def aes_protocol(self):
        self.start_transmission()
        self.send("key")
        s_key = self.receive(int)
        c_rand_num = rsa.crypt(random_number(80), s_key)
        self.send(f"aes|{c_rand_num}|{self.pub_key}")
        s_rand_num = rsa.crypt(int(self.receive()), self.priv_key)
        self.server_aes_key = to_bytes(c_rand_num) + to_bytes(s_rand_num) if s_rand_num != -1 else None
        self.end_transmission()

    def connexion(self, new: bool) -> bool:
        if new:
            return self.sign_up()
        return self.login()

    def header(self, data: bytes) -> bytes:
        message_header = to_bytes(len(data))
        return b'\x00' * (self.HEADER_LENGTH - len(message_header)) + message_header

    def receive(self, target_type: type = str):
        while True:
            try:
                message_header = self.server_socket.recv(self.HEADER_LENGTH)
                if not len(message_header):
                    return False
                message_length = from_bytes(message_header, int)
                return from_bytes(self.server_socket.recv(message_length), target_type)
            except IOError as e:
                if e.errno != errno.EAGAIN and e.errno != errno.EWOULDBLOCK:
                    print('Reading error: {}'.format(str(e)))
                    sys.exit()  # TODO: handle this
            except Exception as e:
                print('Reading error: '.format(str(e)))
                sys.exit()  # TODO: handle this

    def receive_aes(self) -> str:
        return aes.decrypt(self.receive(), self.server_aes_key)

    def send(self, data):
        data = to_bytes(data)
        self.server_socket.send(self.header(data) + data)

    def send_aes(self, data):
        self.send(aes.encrypt(str(data), self.server_aes_key))

    def ping_server(self):
        self.send("")
        self.last_ping = time.time()

    def login(self):
        self.send(aes.encrypt(f"login|{self.username}", self.server_aes_key))
        data = int(aes.decrypt(self.receive(), self.server_aes_key))
        if data == -1:
            return False
        check = rsa.crypt(data, self.priv_key)
        self.send_aes(f"check|{check}")
        if self.receive() == "0":
            return True
        return 1

    def sign_up(self):
        self.send(aes.encrypt(f"sign up|{self.pub_key}|{self.username}", self.server_aes_key))
        return self.receive() == "0"

    def get_friends(self):
        self.send_aes("get friend")
        data = self.receive_aes()
        while len(data) > 0:
            size_username, data = data.split("|", 1)
            username, data = data[:int(size_username)], data[int(size_username) + 1:]
            if username not in self.keys:
                self.get_aes_key(username)

    def get_aes_key(self, friend: str):
        self.send_aes(f"get aes key|{friend}")
        data = self.receive()
        if data == "-1":
            return
        size_key_1, data = data.split("|", 1)
        self.keys[friend] = to_bytes(int(data[:int(size_key_1)])) + to_bytes(int(data[int(size_key_1) + 1:]))

    @staticmethod
    def split_usernames(data: str) -> list:
        usernames = []
        while len(data) > 0:
            size_username, data = data.split("|", 1)
            username, data = data[:int(size_username)], data[int(size_username) + 1:]
            usernames.append(username)

    def get_requests(self):
        self.send_aes("get pendings")
        data = self.receive_aes()
        # data = "USERNAME_LENGTH|USERNAME|USERNAME_LENGTH|USERNAME|..."
        self.requests = self.split_usernames(data)

    def get_pendings(self):
        self.send_aes("get pendings")
        data = self.receive_aes()
        # data = "USERNAME_LENGTH|USERNAME|USERNAME_LENGTH|USERNAME|..."
        self.pendings = self.split_usernames(data)

    def friend_request(self, _friend):
        self.send(encrypt("friendrequest|" + _friend, self.s_key))
        return self.receive()

    def friend_accept(self, _friend):
        self.send(encrypt("friendaccept|" + _friend, self.s_key))
        return self.receive()

    def send_message(self, _friend, _message):
        self.send(encrypt("message|" + _friend + "|" + encrypt(_message, self.get_friend_key(_friend)), self.s_key))
        a = self.receive()
        if a == "-1":
            return -1
        if a == "1":
            return 1
        return datetime.datetime.strptime(a, '%Y-%m-%d %H:%M:%S')

    def get_friend_key(self, _friend):
        self.send(encrypt("getfriendkey|" + _friend, self.s_key))
        a = decrypt(self.receive(), self.priv_key).split("|")
        return int(a[0]), int(a[1])


# sign_up() -> 1:username déjà pris , 0:compte correctement créé, -1: erreur envoi serveur
# login() -> 1:mauvais id ou mdp pour ce compte, 0:compte correctement connecté, -1: erreur envoi serveur

if __name__ == "__main__":
    _username = "bob"
    password = ""
    _pub_key, _priv_key = get_key_from_password(_username + password)
    client = Client(_username, _pub_key, _priv_key, new=True)
    print(password, len(password))
    print(client.is_connected)
    print(client.get_friend())
    print(client.get_pending())
    print(client.get_request())
    print(client.send_message("admin", "salut"))
