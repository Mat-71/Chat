import socket
import json
import time
import select
from key_generator import get_key_from_password, random_number
import rsa
import aes
from User import User
from conversion import to_bytes, from_bytes


# TODO: timeout for socket
# TODO: 2 requests = friends

class Server:
    def __init__(self, ip: str, port: int, password: str, key_size: int = 4096):
        self.IP: str = ip
        self.PORT = port
        self.HEADER_LENGTH = 10
        self.AES_LENGTH = 80
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server_socket.bind((self.IP, self.PORT))
        self.server_socket.listen()
        self.sockets_list = [self.server_socket]
        self.users: dict[str, User] = {}
        self.clients = {}
        """example: self.users = {"username": User(username="username", pub_key=pub_key)} self.clients = {socket: {
        "username": username, "aes_key": aes_key, "check": check, "public_key": public_key, "auth": auth}} """
        self.public_key, self.private_key = get_key_from_password(password, key_size)
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

    def receive(self, client: socket.socket, target_type: type = str):
        try:
            message_header = client.recv(self.HEADER_LENGTH)
            if not len(message_header):
                return False
            message_length = from_bytes(message_header, int)
            message = b''
            while message_length > 0:
                new_part = client.recv(message_length)
                message_length -= len(new_part)
                message += new_part
            return from_bytes(message, target_type)
        except Exception as e:
            print("Exception (receive):", e)
            return False

    def header(self, data: bytes) -> bytes:
        message_header = to_bytes(len(data))
        return b'\x00' * (self.HEADER_LENGTH - len(message_header)) + message_header

    def send(self, data, client: socket.socket):
        data = to_bytes(data)
        client.send(self.header(data) + data)

    def send_aes(self, data, aes_key: bytes, client: socket.socket):
        print("sent:", data)
        self.send(aes.encrypt(str(data), aes_key), client)

    def send_success(self, client: socket.socket, key: bytes):
        self.send_aes(0, key, client)

    def send_fail(self, client: socket.socket, key: bytes, error_code: int = -1):
        self.send_aes(error_code, key, client)

    def send_public_key(self, client: socket.socket):
        self.send(self.public_key, client)

    def aes_protocol(self, client: socket.socket, data: str):
        # data = "RAND_NUM|PUB_KEY"
        print("received:", data)
        c_rand_num, c_pub_key = data.split("|", 1)
        c_rand_num = rsa.crypt(int(c_rand_num), self.private_key)
        c_pub_key = rsa.crypt(int(c_pub_key), self.private_key)
        s_rand_num = random_number(self.AES_LENGTH)
        aes_key = to_bytes(c_rand_num) + to_bytes(s_rand_num)
        self.clients[client] = {"aes_key": aes_key, "auth": False}
        self.send(rsa.crypt(s_rand_num, c_pub_key), client)

    def login(self, client_data: dict, aes_key: bytes, client: socket.socket, username: str):
        # data = "USERNAME"
        if username not in self.users:
            return self.send_fail(client, aes_key)
        _check = random_number(256)
        client_data['check'] = _check
        client_data['username'] = username
        client_data["auth"] = False
        key = self.users[username].pub_key
        self.send_aes(rsa.crypt(_check, key), aes_key, client)

    def check_login(self, client_data: dict, client: socket.socket, aes_key: bytes, check: int):
        # data = "CHECK"
        if "check" not in client_data or "username" not in client_data:
            return
        if client_data["check"] != check:
            return self.send_fail(client, aes_key, 1)
        self.send_success(client, aes_key)
        print('Accepted new connection from {}'.format(client_data["username"]))
        client_data["auth"] = True

    def sign_up(self, client_data: dict, aes_key: bytes, client: socket.socket, data: str):
        # data = "sign up|USER_PUB_KEY|USERNAME"
        user_pub_key, username = data.split("|", 1)
        user_pub_key = int(user_pub_key)
        if username in self.users:
            return self.send_fail(client, aes_key, 1)
        if user_pub_key <= 0 or len(username) < 3:
            return self.send_fail(client, aes_key, 2)
        client_data['username'] = username
        client_data['auth'] = True
        self.users[username] = User(username, user_pub_key)
        print('Accepted new connection from {}'.format(username))
        self.send_success(client, aes_key)

    def request_friend(self, aes_key: bytes, client: socket.socket, user: User, data: str):
        friend_name, key_user, key_friend = data.rsplit("|", 2)
        if friend_name not in self.users or friend_name == user.username or friend_name in user.keys:
            return self.send_fail(client, aes_key, 1)
        if friend_name in user.requests:
            return self.send_fail(client, aes_key, 2)
        if user.username in self.users[friend_name].requests:
            return self.accept_friend(aes_key, client, user, friend_name)
        self.users[friend_name].add_request(user.username, key_friend)
        user.add_pending(friend_name, key_user)
        self.send_success(client, aes_key)

    def accept_friend(self, aes_key: bytes, client: socket.socket, user: User, data: str):
        friend_name, key_user, key_friend = data.rsplit("|", 2)
        if friend_name not in user.get_requests():
            return self.send_fail(client, aes_key, 1)
        user.add_friend(friend_name, key_user)
        self.users[friend_name].add_friend(user.username, key_friend)
        self.send_success(client, aes_key)

    def get_pub_key(self, client: socket.socket, aes_key: bytes, friend_name: str):
        if friend_name not in self.users:
            return self.send_fail(client, aes_key, 1)
        self.send_aes(self.users[friend_name].pub_key, aes_key, client)

    def get_aes_key(self, client: socket.socket, aes_key: bytes, user: User, friend_name: str):
        if friend_name not in user.keys:
            return self.send_fail(client, aes_key, 1)
        self.send_aes(user.get_aes_key(friend_name), aes_key, client)

    def message_reception(self, client: socket.socket, aes_key: bytes, user: User, data: str):
        # data = "USERNAME_LENGTH|USERNAME|CONTENT"
        username_length, data = data.split("|", 1)
        friend, content = data[:int(username_length)], data[int(username_length) + 1:]
        if friend not in user.keys:
            return self.send_fail(client, aes_key, 1)
        sent_time = self.users[friend].new_message(content, user.username)
        self.send_aes(sent_time, aes_key, client)

    def aes_data_receive(self, client: socket.socket, data: str):
        client_data = self.clients[client]
        aes_key = client_data["aes_key"]
        data = aes.decrypt(to_bytes(data), aes_key)
        print("received:", data)
        action = data.split("|", 1)[0]
        data = data.removeprefix(action).removeprefix('|')
        match action:
            case 'login':
                return self.login(client_data, aes_key, client, data)
            case 'check':
                return self.check_login(client_data, client, aes_key, int(data))
            case 'sign up':
                # TODO: check if user password is strong enough (shhhhhhhh!!!!)
                return self.sign_up(client_data, aes_key, client, data)
        if "username" not in client_data or not client_data["auth"]:
            return self.send_fail(client, aes_key)
        user = self.users[client_data["username"]]
        match action:
            case 'get friends':
                return self.send_aes(user.get_friends(), aes_key, client)
            case 'request friend':
                return self.request_friend(aes_key, client, user, data)
            case 'get requests':
                return self.send_aes(user.get_requests(), aes_key, client)
            case 'accept friend':
                return self.accept_friend(aes_key, client, user, data)
            case 'get pending':
                return self.send_aes(user.get_pending(), aes_key, client)
            case 'get pub key':
                return self.get_pub_key(client, aes_key, data)
            case 'get aes key':
                return self.get_aes_key(client, aes_key, user, data)
            case 'send message':
                return self.message_reception(client, aes_key, user, data)
            case "get messages":
                return self.send_aes(user.get_messages(), aes_key, client)
            case _:
                return self.send_fail(client, aes_key)

    def listen_client(self, client: socket.socket, data: str):
        if not data:
            return self.sockets_list.remove(client)
        if data == 'key':  # send key to client
            return self.send_public_key(client)
        if data.startswith("aes"):  # server send aes key to client
            print("received aes key:", data)
            return self.aes_protocol(client, data.removeprefix("aes").removeprefix('|'))
        if client in self.clients:  # connection is secure
            self.aes_data_receive(client, data)
        else:
            self.send("-1", client)

    def listen(self):
        read_sockets, _, exception_sockets = select.select(self.sockets_list, [], self.sockets_list)
        for notified_socket in read_sockets:
            if notified_socket == self.server_socket:
                self.sockets_list.append(self.server_socket.accept()[0])
            else:
                self.listen_client(notified_socket, self.receive(notified_socket))
        for notified_socket in exception_sockets:
            self.sockets_list.remove(notified_socket)
            print("Socket {} is offline".format(notified_socket))
            if notified_socket in self.clients:
                del self.clients[notified_socket]


if __name__ == "__main__":
    server = Server("", 4040, "5")
    print(f'Listening for connections on {server.IP}: {server.PORT}...')
    while True:
        server.listen()
        server.save()
