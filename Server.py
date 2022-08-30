import subprocess
from datetime import datetime
from json import load, dumps
from socket import socket, AF_INET, SOCK_STREAM, SOL_SOCKET, SO_REUSEADDR
from time import time
from select import select
import logging

from Conversion import to_bytes, from_bytes
from Rsa import rsa_crypt
from KeyGenerator import get_key_from_password, random_number
from Aes import encrypt, decrypt
from User import User


# TODO: timeout for socket
# [R] - received
# [S] - sent
# [REG] - sign in
# [LOG] - log in
# [OUT] - sign out
# [AES] - AES encrypted
# [T] - duration of function
# [UNK] - unknown
# [EXC] - exception
# [LOAD] - Load file

class Server:
    def __init__(self, ip: str, port: int, password: str, key_size: int = 4096):
        self.IP: str = ip
        self.PORT = port
        self.HEADER_LENGTH = 10
        self.AES_LENGTH = 80
        self.server_socket = socket(AF_INET, SOCK_STREAM)
        self.server_socket.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
        self.server_socket.bind((self.IP, self.PORT))
        self.server_socket.listen()
        self.sockets_list = [self.server_socket]
        self.users: dict[str, User] = {}
        self.clients = {}
        """example: self.users = {"username": User(username="username", pub_key=pub_key)} self.clients = {socket: {
        "username": username, "aes_key": aes_key, "check": check, "public_key": public_key, "auth": auth}} """
        self.file_number = 0
        self.public_key = self.load()
        self.public_key, self.private_key = get_key_from_password("server", password, self.public_key, key_size)

    @staticmethod
    def get_time(args: list[str]) -> tuple[bool, int]:
        date = datetime.now()
        if len(args) == 1:
            match args[0]:
                case "all":
                    return True, 0
                case "today":
                    return True, int((date.replace(hour=0, minute=0, second=0, microsecond=0)).timestamp() * 1_000)
                case _:
                    return False, 2
        match args[0]:
            case "-a":  # absolute time:
                difference = False
            case "-r":  # relative time:
                difference = True
            case _:
                return False, 2
        date_dict = {
            "y": date.year,
            "m": date.month,
            "d": date.day,
            "h": date.hour,
            "M": date.minute,
            "s": date.second
        }
        for component in args:
            if len(component) < 2 or not component[:-1].isdigit():
                return False, 2
            value, unit = int(component[:-1]), component[-1]
            if unit in date_dict.keys():
                date_dict[unit] = date_dict[unit] - value if difference else value
            else:
                return False, 2
        start = datetime(date_dict["y"], date_dict["m"], date_dict["d"], date_dict["h"], date_dict["M"], date_dict["s"])
        return True, int(start.timestamp() * 1_000)

    def load(self):
        data = None
        for i in range(3):
            try:
                with open(f"ServerSave{i}.json") as jsonFile:
                    users_2 = load(jsonFile)
                    jsonFile.close()
                if data is None:
                    data = users_2
                else:
                    if data[0] < users_2[0]:
                        data = users_2
                        self.file_number = (i + 1) % 3
            except IOError:
                pass
        logger.info(f"[LOAD] save file {self.file_number}")
        self.users = {}
        if data is None:
            return
        for user in data[1]:
            self.users[user['username']] = User(**user)
            if user['username'] == "admin":
                self.users[user['username']].admin_level = 2
        return data[2] if len(data) > 2 else None

    def save(self):
        file_name = f"ServerSave{str(self.file_number)}.json"
        self.file_number = (self.file_number + 1) % 3
        with open(file_name, 'w') as outfile:
            outfile.write(
                dumps([int(time() * 1000), [u.__dict__() for u in self.users.values()], self.public_key], indent=2))

    def receive(self, client: socket, target_type: type = str):
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
            logger.error(f"[R-EXC] {e}")
            return False

    def header(self, data: bytes) -> bytes:
        message_header = to_bytes(len(data))
        return b'\x00' * (self.HEADER_LENGTH - len(message_header)) + message_header

    def send(self, data, client: socket, aes=False):
        if not aes:
            logger.info(f"[S] {data}")
        data = to_bytes(data)
        client.send(self.header(data) + data)

    def send_aes(self, data, aes_key: int, client: socket):
        logger.info(f"[S-AES] {data}")
        self.send(encrypt(str(data), aes_key), client, True)

    def send_success(self, client: socket, aes_key: int):
        self.send_aes(0, aes_key, client)

    def send_fail(self, client: socket, aes_key: int, error_code: int = -1):
        self.send_aes(error_code, aes_key, client)

    def send_public_key(self, client: socket):
        self.send(self.public_key, client)

    def aes_protocol(self, client: socket, data: str):
        # data = "RAND_NUM|PUB_KEY"
        c_rand_num, c_pub_key = data.split("|", 1)
        c_rand_num = rsa_crypt(int(c_rand_num), self.private_key)
        c_pub_key = rsa_crypt(int(c_pub_key), self.private_key)
        s_rand_num = random_number(self.AES_LENGTH)
        aes_key = from_bytes(to_bytes(c_rand_num) + to_bytes(s_rand_num), int)
        self.clients[client] = {"aes_key": aes_key, "auth": False}
        self.send(rsa_crypt(s_rand_num, c_pub_key), client)

    def login(self, client_data: dict, aes_key: int, client: socket, username: str):
        # data = "USERNAME"
        if username not in self.users:
            return self.send_fail(client, aes_key)
        _check = random_number(256)
        client_data['check'] = _check
        client_data['username'] = username
        client_data["auth"] = False
        key = self.users[username].pub_key
        self.send_aes(rsa_crypt(_check, key), aes_key, client)

    def check_login(self, client_data: dict, client: socket, aes_key: int, check: int):
        # data = "CHECK"
        if "check" not in client_data or "username" not in client_data:
            return
        if client_data["check"] != check:
            return self.send_fail(client, aes_key, 1)
        self.send_success(client, aes_key)
        logger.info(f"[LOG] {client_data['username']}")
        client_data["auth"] = True

    def sign_up(self, client_data: dict, aes_key: int, client: socket, data: str):
        # data = "sign up|USER_PUB_KEY|USERNAME"
        user_pub_key, username = data.split("|", 1)
        user_pub_key = int(user_pub_key)
        check = user_pub_key < 0
        user_pub_key = abs(user_pub_key)
        if username in self.users:
            return self.send_fail(client, aes_key, 1)
        if (len(username) < 3) and not check:  # TODO: add more complex username check
            return self.send_fail(client, aes_key, 2)
        client_data['username'] = username
        client_data['auth'] = True
        self.users[username] = User(username, user_pub_key)
        logger.info(f"[REG] {client_data['username']}")
        self.send_success(client, aes_key)

    def log_out(self, client: socket, aes_key: int):
        logger.info(f"[OUT] {self.clients.pop(client)['username']}")
        self.send_success(client, aes_key)
        client.close()

    def request_friend(self, aes_key: int, client: socket, user: User, data: str):
        friend_name, key_user, key_friend = data.rsplit("|", 2)
        if friend_name not in self.users or friend_name == user.username or friend_name in user.keys:
            return self.send_fail(client, aes_key, 1)
        if friend_name in user.requests:
            return self.send_fail(client, aes_key, 2)
        if user.username in self.users[friend_name].requests:
            return self.accept_friend(aes_key, client, user, friend_name)
        if user.admin_level > 0:
            num = random_number(self.AES_LENGTH)
            friend = self.users[friend_name]
            friend.keys[user.username] = [key_friend, rsa_crypt(num, friend.pub_key)]
            user.keys[user.username] = [key_user, rsa_crypt(num, user.pub_key)]
            return self.send_success(client, aes_key)
        self.users[friend_name].add_request(user.username, key_friend)
        user.add_pending(friend_name, key_user)
        self.send_success(client, aes_key)

    def accept_friend(self, aes_key: int, client: socket, user: User, data: str):
        friend_name, key_user, key_friend = data.rsplit("|", 2)
        if friend_name not in user.get_requests():
            return self.send_fail(client, aes_key, 1)
        user.add_friend(friend_name, key_user)
        self.users[friend_name].add_friend(user.username, key_friend)
        self.send_success(client, aes_key)

    def get_pub_key(self, client: socket, aes_key: int, friend_name: str):
        if friend_name not in self.users:
            return self.send_fail(client, aes_key, 1)
        self.send_aes(self.users[friend_name].pub_key, aes_key, client)

    def get_aes_key(self, client: socket, aes_key: int, user: User, friend_name: str):
        if friend_name not in user.keys:
            return self.send_fail(client, aes_key, 1)
        self.send_aes(user.get_aes_key(friend_name), aes_key, client)

    def message_reception(self, client: socket, aes_key: int, user: User, data: str):
        # data = "USERNAME_LENGTH|USERNAME|CONTENT"
        username_length, data = data.split("|", 1)
        friend, content = data[:int(username_length)], data[int(username_length) + 1:]
        if friend not in user.keys:
            return self.send_fail(client, aes_key, 1)
        sent_time = self.users[friend].new_message(content, user.username)
        self.send_aes(sent_time, aes_key, client)

    def admin_command(self, client: socket, aes_key: int, user: User, data: str):
        # TODO: add more commands
        # data = "COMMAND ARGS"
        if user.admin_level < 1:
            return self.send_fail(client, aes_key)
        command = data.split(" ", 1)[0]
        args = data.removeprefix(command).removeprefix(' ').split(" ")
        # fails:
        # 1 - unknown command
        # 2 - unexpected argument or missing argument
        # 3 - unknown user
        # 4 - no permission
        match command:
            case "shutdown":
                if len(args) > 0:
                    return self.send_fail(client, aes_key, 2)
                self.send_success(client, aes_key)
                return self.shutdown()
            case "restart":
                self.send_success(client, aes_key)
                return self.restart()
            case "promote":
                # args = "LEVEL USERNAME"
                level, username = args
                if not level.removeprefix('-').isdigit():
                    return self.send_fail(client, aes_key, 2)
                if username not in self.users:
                    return self.send_fail(client, aes_key, 3)
                if int(level) >= user.admin_level:
                    return self.send_fail(client, aes_key, 4)
                self.users[username].admin_level = int(level)
                return self.send_success(client, aes_key)
            case "getlogs":
                if len(args) < 2:
                    return self.send_fail(client, 2)
                success, value = Server.get_time(args, False)
                # TODO: do things
            case _:
                return self.send_fail(client, aes_key, 1)

    def aes_data_receive(self, client: socket, data: str):
        client_data = self.clients[client]
        aes_key = client_data["aes_key"]
        data = decrypt(to_bytes(data), aes_key)
        logger.info(f"[R-AES] {data}")
        action = data.split("|", 1)[0]
        data = data.removeprefix(action).removeprefix('|')
        match action:
            case 'login':
                return self.login(client_data, aes_key, client, data)
            case 'check':
                return self.check_login(client_data, client, aes_key, int(data))
            case 'sign up':
                return self.sign_up(client_data, aes_key, client, data)
        if "username" not in client_data or not client_data["auth"]:
            return self.send_fail(client, aes_key)
        user = self.users[client_data["username"]]
        match action:
            case "log out":
                return self.log_out(client, aes_key)
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
            case "get admin level":
                return self.send_aes(user.admin_level, aes_key, client)
            case "admin":
                return self.admin(client, aes_key, user, data)
            case _:
                logger.warning(f"[R-AES-UNK] Unknown action {action}")
                return self.send_fail(client, aes_key)

    def listen_client(self, client: socket, data: str):
        try:
            if not data:
                return self.sockets_list.remove(client)
            if data == 'key':  # send key to client
                logger.info("[R] key")
                return self.send_public_key(client)
            if data.startswith("aes"):  # server send aes key to client
                logger.info(f"[R] {data}")
                return self.aes_protocol(client, data.removeprefix("aes").removeprefix('|'))
            if client in self.clients:  # connection is secure
                self.aes_data_receive(client, data)
            else:
                logger.warning(f"[R-UNK] {data}")
                self.send("-1", client)
        except Exception as e:
            logger.error(f"[ERR] {e}")

    def listen(self):
        read_sockets, _, exception_sockets = select(self.sockets_list, [], self.sockets_list)
        for notified_socket in read_sockets:
            start = time()
            if notified_socket == self.server_socket:
                self.sockets_list.append(self.server_socket.accept()[0])
            else:
                self.listen_client(notified_socket, self.receive(notified_socket))
            logger.debug(f"[T] listen_client: {time() - start}")
        for notified_socket in exception_sockets:
            self.sockets_list.remove(notified_socket)
            logger.warning(f"[OUT] offline socket: {notified_socket}")
            if notified_socket in self.clients:
                del self.clients[notified_socket]

    def shutdown(self, close_server=True):
        for client in self.clients:
            client.close()
        self.server_socket.close()
        self.save()
        logger.warning("[OUT] Server shutdown")
        if close_server:
            exit(0)

    def restart(self):
        self.shutdown(False)
        logger.warning("[OUT] Server restart")
        subprocess.run(["python3.10", "Server.py", "&"])
        exit(0)


if __name__ == "__main__":
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)

    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')

    fh = logging.FileHandler('logs_server.log')
    fh.setLevel(logging.DEBUG)
    fh.setFormatter(formatter)
    logger.addHandler(fh)

    sh = logging.StreamHandler()
    sh.setLevel(logging.DEBUG)
    sh.setFormatter(formatter)
    logger.addHandler(sh)

    server = Server("", 4040, "fastPassword")
    logger.info("Listening on port 4040")
    while True:
        server.listen()
        server.save()
