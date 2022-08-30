import sys
from errno import EAGAIN, EWOULDBLOCK
from json import loads, dumps
from os import path, getcwd, makedirs
from socket import SOCK_STREAM, socket, AF_INET
from time import time

from Aes import encrypt, decrypt
from Conversion import to_bytes as conv_to_bytes, from_bytes as conv_from_bytes
from EncryptFile import encrypt_file, decrypt_file
from KeyGenerator import get_key_from_password, random_number
from Rsa import rsa_crypt as rsa_crypt


# TODO: timeout for socket

class Client:
    def __init__(self, _username: str, password: str, new: bool = False):
        self.server_address = ("172.105.6.165", 4040)
        self.HEADER_LENGTH = 10
        self.AES_LENGTH = 80
        self.server_socket = socket(AF_INET, SOCK_STREAM)
        self.server_socket.connect(self.server_address)
        self.server_socket.setblocking(False)
        self.username = _username
        self.public_key, self.private_key = get_key_from_password(_username, password,
                                                                  key_size=128 if _username == "test" else 2048)
        self.messages = {}  # messages = {friend: [message, message, message]}
        self.keys: dict[str, int] = {}  # key = {"username": aes_key}
        self.requests = []  # requests = [username, username, username]
        self.pending = []  # pending = [username, username, username]
        self.is_connected = -1
        self.server_aes_key = None
        self.last_ping = time()
        self.last_log = None

        self.aes_protocol()
        if self.server_aes_key is None:
            return
        self.is_connected = 0
        self.sign_up() if new else self.login()
        if self.last_log != 0:
            return
        self.is_connected = 1
        if not new:
            self.load()

    def __dict__(self):
        return {
            "username": self.username,
            "messages": self.messages,
            "keys": self.keys,
            "requests": self.requests,
            "pending": self.pending
        }

    def load(self):
        # load messages, keys, requests, pending from json file "[self.username].json" in the same directory
        content = decrypt_file(self.username, self.private_key[1])
        if content is None:
            return
        data = loads(content)
        self.messages = data["messages"]
        self.keys = data["keys"]
        self.requests = data["requests"]
        self.pending = data["pending"]

    def save(self):
        # save messages, keys, requests, pending to json file "[self.username].json" in the same directory
        content = dumps(self.__dict__())
        file_name, encrypted = encrypt_file(self.username, self.private_key[1], content)
        path_directory = path.join(getcwd(), "Saves")
        if not path.exists(path_directory):
            makedirs(path_directory)
        file_path = path.join(path_directory, file_name)
        with open(file_path, "wb") as f:
            f.write(encrypted)

    def start_transmission(self):
        self.server_socket = socket(AF_INET, SOCK_STREAM)
        self.server_socket.connect(self.server_address)
        self.server_socket.setblocking(False)

    def end_transmission(self):
        self.server_socket.close()

    def aes_protocol(self):
        self.send("key")
        s_key = self.receive(int)
        c_rand_num = random_number(self.AES_LENGTH)
        self.send(f"aes|{rsa_crypt(c_rand_num, s_key)}|{rsa_crypt(self.public_key, s_key)}")
        s_rand_num = rsa_crypt(self.receive(int), self.private_key)
        self.server_aes_key = conv_to_bytes(c_rand_num) + conv_to_bytes(s_rand_num) if s_rand_num != -1 else None

    def header(self, data: bytes) -> bytes:
        message_header = conv_to_bytes(len(data))
        return b'\x00' * (self.HEADER_LENGTH - len(message_header)) + message_header

    def receive(self, target_type: type = str):
        message_header = None
        message = b''
        message_length = 0
        while True:
            try:
                if message_header is None:
                    message_header = self.server_socket.recv(self.HEADER_LENGTH)
                    if not len(message_header):
                        return False
                    message_length = conv_from_bytes(message_header, int)
                while message_length > 0:
                    new_part = self.server_socket.recv(min(message_length, 512))
                    message_length -= len(new_part)
                    message += new_part
                self.last_ping = time()
                return conv_from_bytes(message, target_type)
            except IOError as e:
                if e.errno != EAGAIN and e.errno != EWOULDBLOCK:
                    print(f'Reading error: {str(e)}')
                    sys.exit()  # TODO: handle this
            except Exception as e:
                print(f'Reading error: {str(e)}')
                sys.exit()  # TODO: handle this

    def receive_aes(self) -> str:
        data = decrypt(self.receive(bytes), self.server_aes_key)
        print("received:", data)
        return data

    def send(self, data):
        data = conv_to_bytes(data)
        self.server_socket.send(self.header(data) + data)

    def send_aes(self, data):
        print("sent:", str(data))
        self.send(encrypt(str(data), self.server_aes_key))

    def ping_server(self):
        self.send("")
        self.last_ping = time()

    def login(self):
        self.send_aes(f"login|{self.username}")
        data = int(self.receive_aes())
        if data == -1:
            self.last_log = -1
            return
        check = rsa_crypt(data, self.private_key)
        self.send_aes(f"check|{check}")
        self.last_log = int(self.receive_aes())

    def sign_up(self):
        self.send_aes(f"sign up|-{self.public_key}|{self.username}")
        self.last_log = int(self.receive_aes())

    def get_friends(self):
        self.send_aes("get friends")
        data = self.receive_aes()
        for username in self.split_data(data):
            if username not in self.keys:
                self.get_aes_key(username)
                if username not in self.messages:
                    self.messages[username] = []

    def get_aes_key(self, friend: str):
        self.send_aes(f"get aes key|{friend}")
        data = self.receive_aes()
        if data == "-1":
            return
        key_1, key_2 = data.split("|", 1)
        key_1 = rsa_crypt(int(key_1), self.private_key)
        key_2 = rsa_crypt(int(key_2), self.private_key)
        self.keys[friend] = conv_from_bytes(conv_to_bytes(key_1) + conv_to_bytes(key_2), int)

    @staticmethod
    def split_data(data: str) -> list[str]:
        splits = []
        while len(data) > 0:
            size_split, data = data.split("|", 1)
            split_data, data = data[:int(size_split)], data[int(size_split) + 1:]
            splits.append(split_data)
        return splits

    def get_requests(self):
        self.send_aes("get requests")
        data = self.receive_aes()
        # data = "USERNAME_LENGTH|USERNAME|USERNAME_LENGTH|USERNAME|..."
        self.requests = self.split_data(data)

    def get_pending(self):
        self.send_aes("get pending")
        data = self.receive_aes()
        # data = "USERNAME_LENGTH|USERNAME|USERNAME_LENGTH|USERNAME|..."
        self.pending = self.split_data(data)

    def generate_key_part(self, friend: str) -> str | None:
        friend_key = self.get_public_key(friend)
        if friend_key == 0:
            return
        rand_num = random_number(self.AES_LENGTH)
        return "|".join([friend, str(rsa_crypt(rand_num, self.public_key)), str(rsa_crypt(rand_num, friend_key))])

    def request_friend(self, friend: str):
        key_part = self.generate_key_part(friend)
        if key_part is None:
            return
        self.send_aes(f'request friend|{key_part}')
        self.last_log = int(self.receive_aes())

    def accept_friend(self, friend: str):
        key_part = self.generate_key_part(friend)
        if key_part is None:
            return
        self.send_aes(f'accept friend|{key_part}')
        self.last_log = int(self.receive_aes())

    def get_public_key(self, username: str) -> int:
        self.send_aes(f"get pub key|{username}")
        data = int(self.receive_aes())
        if data == -1:
            self.last_log = -1
            return 0
        return data

    def insert_message(self, friend: str, new_message: dict):
        # slow method
        if friend not in self.messages:
            self.messages[friend] = []
        messages = self.messages[friend]
        for message in messages:
            if message["sent_time"] == new_message["sent_time"]:
                return
        messages.append(new_message)
        i = len(messages) - 2
        while i >= 0 and messages[i]["sent_time"] > new_message["sent_time"]:
            messages[i], messages[i + 1] = messages[i + 1], messages[i]
            i -= 1

    def send_message(self, friend: str, message: str):
        if friend not in self.keys:
            self.get_aes_key(friend)
        aes_key = self.keys[friend] if friend in self.keys else None  # if is not friend, aes_key is None
        if aes_key is None:
            return -1
        self.send_aes(f"send message|{len(friend)}|{friend}|{conv_from_bytes(encrypt(message, aes_key), str)}")
        data = int(self.receive_aes())
        if data < 0:
            self.last_log = data
            return
        dict_message = {"sent_time": data, "content": message, "sender": self.username}
        self.insert_message(friend, dict_message)

    def get_messages(self):
        self.send_aes("get messages")
        data = self.receive_aes()
        messages = self.split_data(data)
        for message in messages:
            sent_time, size_username, message = message.split("|", 2)
            username, content = message[:int(size_username)], message[int(size_username) + 1:]
            if username not in self.keys:
                self.get_aes_key(username)
            sent_time = int(sent_time)
            content = decrypt(conv_to_bytes(content), self.keys[username])
            dict_message = {"sent_time": sent_time, "content": content, "sender": username}
            self.insert_message(username, dict_message)

    def get_admin_level(self):
        self.send_aes("get admin level")
        return int(self.receive_aes())

    def log_out(self):
        self.send_aes("log out")
        self.last_log = int(self.receive_aes())
        self.save()


if __name__ == "__main__":
    admin = Client("admin", "admin", False)
    print(admin.pending)
    admin.get_pending()
    print(admin.pending)
    admin.save()
