import pickle
import socket
import threading
import select

# user = pickle.load(open("user.p", "rb"))
user = {}
# session = pickle.load(open("session.p", "rb"))
session = {}
running = True


class ThreadForClient(threading.Thread):
    def __init__(self, conn):
        threading.Thread.__init__(self)
        self.conn = conn
        self.session = None
        self.user = None

    def run(self):
        global running
        data = self.conn.recv(1024)
        data = data.decode("utf-8")
        send_ = '0'
        if data[0] == '|':
            data = data[1:].split('|')
            if data[0] == 'login' and len(data) == 3:
                print(user[data[1]][0], data[2])
                if data[1] in user:
                    if user[data[1]][0] == data[2]:
                        send_ = '1'
                        self.user = data[1]
                        print(self.user + " viens de se connecter")
            elif data[0] == 'newlogin' and len(data) == 3:
                if not data[1] in user:
                    user[data[1]] = [data[2], []]
                    send_ = '1'
                    self.user = data[1]
                    print(self.user + " viens de se connecter")
            elif data[0] == 'session' and (len(data) == 2 or len(data) == 3):
                if data[1] in user[self.user][1]:
                    self.session = data[1]
                    send_ = '1'
                if data[1] in session and len(data) == 3:
                    if session[data[1]][0] == data[2]:
                        send_ = '1'
                        self.session = data[1]
                        user[self.user][1].append(data[1])
            elif data[0] == 'newsession' and len(data) == 3:
                if not data[1] in session:
                    session[data[1]] = [data[2], []]
                    send_ = '1'
                    self.session = data[1]
                    user[self.user][1].append(data[1])
            elif self.session in session and self.user in user and data[0] == "getchat":
                if self.session in user[self.user][1]:
                    send_ = ""
                    for i_session in session[self.session][1]:
                        send_ += '|' + i_session[0] + '\\' + i_session[1]
                    send_ = send_[1:]
                else:
                    self.session = None
            elif self.user in user and data[0] == "getsessions":
                send_ = "|"
                for chat in user[self.user][1]:
                    send_ += "|" + chat
                if len(send_) != 1:
                    send_ = send_[1:]
            elif data[0] == 'shutdown':
                running = False
                send_ = 'Arret du serveur'
            self.conn.send(send_.encode("utf-8"))
        elif not (self.user is None or self.session is None):
            session[self.session][1].append([self.user, data])
            print(self.session + ':' + self.user + '>' + data)
        else:
            self.conn.sendall("tu n'es pas connecté".encode("utf-8"))


hote = ''
port = 12800
clients_connectes = []
socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
socket.bind((hote, port))
print("Le serveur est démarré...")
connection = []
while running:
    socket.listen()
    connexions_demandees, wlist, xlist = select.select([socket],
                                                       [], [], 0.05)

    for connexion in connexions_demandees:
        connexion_avec_client, infos_connexion = connexion.accept()
        # On ajoute le socket connecté à la liste des clients
        try:
            connection.append(ThreadForClient(connexion_avec_client))
            clients_connectes.append(connexion_avec_client)
        except ConnectionResetError:
            pass
    clients_a_lire = []
    try:
        clients_a_lire, wlist, xlist = select.select(clients_connectes,
                                                     [], [], 0.05)
    except select.error:
        pass
    else:
        for i in clients_a_lire:
            my_thread = connection[clients_connectes.index(i)]
            try:
                my_thread.run()
            except:
                pass
    pickle.dump(user, open("user.p", "wb"))
    pickle.dump(session, open("session.p", "wb"))
