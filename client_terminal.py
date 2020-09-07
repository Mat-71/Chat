import socket
import time

adresseIP = "172.16.1.69"  # Ici, le poste local
port = 12800  # Se connecter sur le port 50000

message = ""
try:
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect((adresseIP, port))
    print("Connecté au serveur")
    print("Tapez FIN pour terminer la conversation. ")
    running = True
    while running:
        message = input("> ")
        if message.lower() == "fin":
            running = False
        client.send(message.encode("utf-8"))
        time.sleep(0.1)
        client.send(b'|getchat')
        reponse = client.recv(8191).decode("utf-8")
        reponse = reponse.split('|')
        for i in reponse:
            for j in i.split('\\'):
                print(j, end='"')
            print("")
    print("Connexion fermée")
    client.close()
except ConnectionRefusedError:
    print("erreur de connexion")
