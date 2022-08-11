import datetime
import json
import time

import aes
import rsa
from encryption import *
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
        self.requests = {}  # requests = {"username": key}
        self.pendings = {}  # pendings = {"username": key}
        self.is_connected = -1
        self.server_aes_key = None
        self.last_ping = self.ping()
        self.aes_protocol()
        if self.server_aes_key is None:
            return
        self.is_connected = 0
        if not self.connexion(new):
            return
        self.is_connected = 1
        if new:
            self.load()

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
                    sys.exit()
            except Exception as e:
                print('Reading error: '.format(str(e)))
                sys.exit()

    def send(self, data):
        data = to_bytes(data)
        self.server_socket.send(self.header(data) + data)

    def send_aes(self, data):
        self.send(aes.encrypt(str(data), self.server_aes_key))

    def ping(self):
        self.send("")
        return time.time()

    def login(self):
        user = aes.encrypt('login|' + self.username, self.s_key)
        self.send(user)
        check = self.receive()
        if check == "-1":
            return -1
        check = encrypt('check|' + decrypt(check, self.key[1]), self.s_key)
        self.send(check)
        if self.receive() == "0":
            return 0
        return 1

    def sign_up(self):
        self.send(aes.encrypt(f"sign up|{self.pub_key}|{self.username}", self.server_aes_key))
        return self.receive() == "0"

    def get_friend(self):
        self.send(encrypt("getfriend|", self.s_key))
        a = decrypt(self.receive(), self.priv_key)
        return a.split("|") if a != "" else []

    def get_pending(self):
        self.send(encrypt("getpending|", self.s_key))
        a = decrypt(self.receive(), self.key[1])
        return a.split("|") if a != "" else []

    def get_request(self):
        self.send(encrypt("getrequest|", self.s_key))
        a = decrypt(self.receive(), self.priv_key)
        return a.split("|") if a != "" else []

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
    username = "bob"
    password = ""
    _pub_key, _priv_key = get_key_from_password(username + password)
    client = Client(username, _pub_key, _priv_key, new=True)
    print(password, len(password))
    print(client.is_connected)
    print(client.get_friend())
    print(client.get_pending())
    print(client.get_request())
    print(client.send_message("admin", "salut"))
