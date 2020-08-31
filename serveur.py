import pickle
import socket
import threading
import select

user = pickle.load(open("user.p", "rb"))
session = pickle.load(open("session.p", "rb"))
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
        send_ = 'erreur commande'
        if data[0] == '|':
            data = data[1:].split('|')
            if data[0] == 'login' and len(data) == 3:
                if data[1] in user:
                    if user[data[1]][0] == data[2]:
                        send_ = 'Vous etes connecté'
                        self.user = data[1]
                    else:
                        send_ = 'mauvais mot de passe'
                else:
                    send_ = 'login inexistant'
            elif data[0] == 'newlogin' and len(data) == 3:
                if data[1] in user:
                    send_ = 'nom utilisateur déjà pris'
                else:
                    user[data[1]] = [data[2], []]
                    send_ = 'Vous etes connecté'
                    self.user = data[1]
            elif data[0] == 'session' and (len(data) == 2 or len(data) == 3):
                if data[1] in user[self.user][1]:
                    self.session = data[1]
                    send_ = 'Vous etes connecté à la session'
                else:
                    send_ = "Vous n'avez pas acces à la session"
                if data[1] in session and len(data) == 3:
                    if session[data[1]][0] == data[2]:
                        send_ = 'Vous etes connecté à la session'
                        self.session = data[1]
                        user[self.user][1].append(data[1])
                    else:
                        send_ = 'mauvais mot de passe'
                elif len(data) == 3:
                    send_ = 'session inexistante'
            elif data[0] == 'newsession' and len(data) == 3:
                if data[1] in session:
                    send_ = 'nom de session déjà pris'
                else:
                    session[data[1]] = [data[2], []]
                    send_ = 'Vous etes connecté à la session'
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
                    send_ = 'chat error'
            elif self.user in user and data[0] == "getsessions":
                send_ = ""
                for chat in user[self.user][1]:
                    send_ += "|" + i
                send_ = send_[1:]
            elif data[0] == 'shutdown':
                running = False
                send_ = 'Arret du serveur'
            self.conn.sendall(send_.encode("utf-8"))
        elif not (self.user is None or self.session is None):
            print(self.user, self.session)
            session[self.session][1].append([self.user, data])
            print(self.session + ':' + self.user + '>' + data)
            message = self.user + '>' + data
            self.conn.sendall(message.encode("utf-8"))
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
        print(infos_connexion[0] + " vient de se connecter")
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
            except ConnectionResetError:
                pass
    pickle.dump(user, open("user.p", "wb"))
    pickle.dump(session, open("session.p", "wb"))
