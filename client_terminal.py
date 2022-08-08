import datetime

import rsa
from encryption import *
import socket
import sys
import errno
from key_generator import get_key_from_password, random_number
from conversion import to_bytes, from_bytes

sys.setrecursionlimit(15000)


class Client:
    def __init__(self, _username: str, pub_key: int, priv_key: tuple[int, int], new=True):
        self.IP = "localhost"
        self.PORT = 42690
        self.HEADER_LENGTH = 10
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client_socket.connect((self.IP, self.PORT))
        self.client_socket.setblocking(False)
        self.username = _username
        self.pub_key = pub_key
        self.priv_key = priv_key
        self.s_key = 0
        self.is_connected = -1

    def start_protocol(self, new):
        self._send("key")
        self.s_key = int(self.receive())
        if new:
            self.is_connected = self.new_login()
        else:
            self.is_connected = self.login()

    def get_state(self):
        return self.is_connected

    def receive(self):
        while True:
            try:
                header = self.client_socket.recv(self.HEADER_LENGTH)
                if not len(header):
                    print('Connection closed by the server')
                    sys.exit()
                header = int(header.decode('utf-8').strip())
                m = from_bytes(self.client_socket.recv(header), str)
                return m
            except IOError as e:
                if e.errno != errno.EAGAIN and e.errno != errno.EWOULDBLOCK:
                    print('Reading error: {}'.format(str(e)))
                    sys.exit()
            except Exception as e:
                print('Reading error: '.format(str(e)))
                sys.exit()

    def _send(self, _message):
        if type(_message) != bytes:
            _message = bytes(_message, 'utf-8')
        header = f"{len(_message):<{self.HEADER_LENGTH}}".encode('utf-8')
        self.client_socket.send(header + _message)

    def login(self):
        user = encrypt('login|' + self.username, self.s_key)
        self._send(user)
        check = self.receive()
        if check == "-1":
            return -1
        check = encrypt('check|' + decrypt(check, self.key[1]), self.s_key)
        self._send(check)
        if self.receive() == "0":
            return 0
        return 1

    def new_login(self):
        self._send(encrypt(
            'newlogin|' + str(self.key[0][0]) + "," + str(self.key[0][1]) + "|" + encrypt(self.username, self.key[1]),
            self.s_key))
        a = self.receive()
        if a == '-1':
            return 1
        a = decrypt(a, self.s_key)
        if a == self.username:
            self._send(encrypt("check2|0", self.s_key))
            return 0
        self._send(encrypt("check2|-1", self.s_key))
        return -1

    def get_friend(self):
        self._send(encrypt("getfriend|", self.s_key))
        a = decrypt(self.receive(), self.priv_key)
        return a.split("|") if a != "" else []

    def get_pending(self):
        self._send(encrypt("getpending|", self.s_key))
        a = decrypt(self.receive(), self.key[1])
        return a.split("|") if a != "" else []

    def get_request(self):
        self._send(encrypt("getrequest|", self.s_key))
        a = decrypt(self.receive(), self.priv_key)
        return a.split("|") if a != "" else []

    def friend_request(self, _friend):
        self._send(encrypt("friendrequest|" + _friend, self.s_key))
        return self.receive()

    def friend_accept(self, _friend):
        self._send(encrypt("friendaccept|" + _friend, self.s_key))
        return self.receive()

    def send_message(self, _friend, _message):
        self._send(encrypt("message|" + _friend + "|" + encrypt(_message, self.get_friend_key(_friend)), self.s_key))
        a = self.receive()
        if a == "-1":
            return -1
        if a == "1":
            return 1
        return datetime.datetime.strptime(a, '%Y-%m-%d %H:%M:%S')

    def get_friend_key(self, _friend):
        self._send(encrypt("getfriendkey|" + _friend, self.s_key))
        a = decrypt(self.receive(), self.priv_key).split("|")
        return int(a[0]), int(a[1])


username = "admin"
password = ""
key = get_key_from_password(username + password)
client = Client(username, key, new=False)

# new_login() -> 1:username déjà pris , 0:compte correctement créé, -1: erreur envoi serveur
# login() -> 1:mauvais id ou mdp pour ce compte, 0:compte correctement connecté, -1: erreur envoi serveur

if __name__ == "__main__":
    client = Client(username, pub_key, priv_key, new=True)
    user_randaom_number = random_number(80)
    cypher = rsa.crypt(user_randaom_number)
    print(password, len(password))
    print(client.get_state())
    print(client.get_friend())
    print(client.get_pending())
    print(client.get_request())
    print(client.send_message("a", "salut"))
