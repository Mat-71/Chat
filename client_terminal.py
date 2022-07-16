from encryption import *
import socket
import sys
import errno
from key_generator import get_key_from_password

sys.setrecursionlimit(15000)
HEADER_LENGTH = 10
IP = "localhost"
PORT = 42690
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect((IP, PORT))
client_socket.setblocking(False)


def receive():
    while True:
        try:
            header = client_socket.recv(HEADER_LENGTH)
            if not len(header):
                print('Connection closed by the server')
                sys.exit()
            header = int(header.decode('utf-8').strip())
            m = client_socket.recv(header).decode('utf-8')
            return m
        except IOError as e:
            if e.errno != errno.EAGAIN and e.errno != errno.EWOULDBLOCK:
                print('Reading error: {}'.format(str(e)))
                sys.exit()
        except Exception as e:
            print('Reading error: '.format(str(e)))
            sys.exit()


def send(message):
    header = f"{len(message.encode('utf-8')):<{HEADER_LENGTH}}".encode('utf-8')
    client_socket.send(header + message.encode('utf-8'))


def login(user: str):
    user = encrypt('login|' + user, s_key)
    send(user)
    check = receive()
    if check == "-1":
        return -1
    check = encrypt('check|' + decrypt(check, key[1]), s_key)
    send(check)
    if receive() == "0":
        return 0
    return 1


def new_login(user: str):
    send(encrypt('newlogin|' + str(key[0][0]) + "," + str(key[0][1]) + "|" + encrypt(user, key[1]), s_key))
    a = receive()
    if a == '-1':
        return 1
    a = decrypt(a, s_key)
    if a == user:
        send(encrypt("check2|0", s_key))
        return 0
    send(encrypt("check2|-1", s_key))
    return -1


send("key")
s_key = receive()
s_key = s_key.split(",")
s_key = (int(s_key[0]), int(s_key[1]))

username = input()
password = input()
key = get_key_from_password(username + password)

# new_login(username) -> 1:username pris , 0:compte correctement créé, -1: erreur envoie serveur
# login(username) -> 1:mauvais mdp pour ce compte, 0:compte correctement connecté, -1: identifiant inconnu

if __name__ == "__main__":
    print(new_login(username))
    print(login(username))
