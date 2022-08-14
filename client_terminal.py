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
    def __init__(self, _username: str, public_key: int, private_key: tuple[int, int], new: bool = False):
        self.server_address = ("localhost", 42690)
        self.HEADER_LENGTH = 10
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.connect(self.server_address)
        self.server_socket.setblocking(False)
        self.username = _username
        self.public_key = public_key
        self.private_key = private_key
        self.messages = {}  # messages = {friend: [message, message, message]}
        self.keys = {}  # key = {"username": aes_key}
        self.requests = []  # requests = {"username": key}
        self.pending = []  # pending = {"username": key}
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
        # load messages, keys, requests, pending from json file "[self.username].json" in the same directory
        try:
            with open(self.username + ".json", "r") as f:
                data = json.load(f)
                self.messages = data["messages"]
                self.keys = data["keys"]
                self.requests = data["requests"]
                self.pending = data["pending"]
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
        self.send(f"aes|{c_rand_num}|{self.public_key}")
        s_rand_num = rsa.crypt(int(self.receive()), self.private_key)
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
        check = rsa.crypt(data, self.private_key)
        self.send_aes(f"check|{check}")
        if self.receive() == "0":
            return True
        return 1

    def sign_up(self):
        self.send(aes.encrypt(f"sign up|{self.public_key}|{self.username}", self.server_aes_key))
        return self.receive() == "0"

    def get_friends(self):
        self.send_aes("get friend")
        data = self.receive_aes()
        for username in self.split_usernames(data):
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
        return usernames

    def get_requests(self):
        self.send_aes("get requests")
        data = self.receive_aes()
        # data = "USERNAME_LENGTH|USERNAME|USERNAME_LENGTH|USERNAME|..."
        self.requests = self.split_usernames(data)

    def get_pending(self):
        self.send_aes("get pending")
        data = self.receive_aes()
        # data = "USERNAME_LENGTH|USERNAME|USERNAME_LENGTH|USERNAME|..."
        self.pending = self.split_usernames(data)

    def friend(self, friend: str) -> str:  # TODO: modify the name of this function and variables
        friend_key = self.get_public_key(friend)
        rand_num = random_number(80)
        a = [friend, rsa.crypt(rand_num, self.public_key),
             rsa.crypt(rand_num, friend_key)]
        return "|".join([f"{len(str(name))}|{name}" for name in a])

    def friend_request(self, friend: str) -> int:
        self.send_aes(f'friend request|{self.friend(friend)}')
        return int(self.receive_aes())

    def friend_accept(self, friend: str) -> int:
        self.send_aes(f'accept friend|{self.friend(friend)}')
        return int(self.receive_aes())

    def get_public_key(self, username: str) -> int:
        self.send_aes(f"get pub key|{username}")
        return int(self.receive_aes())

    def send_message(self, friend: str, message: str):
        if friend not in self.keys:
            self.get_aes_key(friend)
        aes_key = self.keys[friend] if friend in self.keys else None  # if is not friend, aes_key is None
        if aes_key is None:
            return -1
        self.send_aes(f"send message|{self.friend(friend)}|{friend}|{aes.encrypt(message, aes_key)}")
        return int(self.receive())


if __name__ == "__main__":
    _username = "bob"
    password = ""
    _public_key, _private_key = get_key_from_password(_username + password)
    client = Client(_username, _public_key, _private_key, new=True)
    print(password, len(password))
    print(client.is_connected)
    print(client.send_message("admin", "salut"))
