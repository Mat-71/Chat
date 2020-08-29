import socket
import threading
import select
message=""
class ThreadForClient(threading.Thread):
    def __init__(self, conn):
        threading.Thread.__init__(self)
        self.conn = conn
        self.session = self.conn.recv(1024).decode("utf-8")
    def run(self):
        global message
        data = self.conn.recv(1024)
        data = data.decode("utf-8")
        message+='|'+data +'\\'+ self.session
        if message[0]=='|':
            message = message[1:]
        print(message)
        self.print_message()
    def print_message(self):
        global message
        temp = message.split('|')
        for i in range(len(temp)):
            temp[i] = temp[i].split('\\')
        send_=""
        for i in temp:
            send_+="|"+i[0]
        send_= send_[1:]
        self.conn.sendall(send_.encode("utf-8"))
hote = ''
port = 12800

clients_connectes = []
socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
socket.bind((hote, port))
print("Le serveur est démarré...")
connection = []
while True:
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
        print(infos_connexion[0]+" vient de se connecter")
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
client.close()
socket.close()




