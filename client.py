import socket

import pygame

pygame.init()
size_screen = pygame.display.Info()
height = size_screen.current_h
width = size_screen.current_w
print(height, width)

Screen = pygame.display.set_mode((width, height), pygame.FULLSCREEN)
#Screen = pygame.display.set_mode((500, 500))
adresseIP = "172.16.1.69"  # Ici, le poste local
port = 12800  # Se connecter sur le port 50000

message = ""
try:
    #client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    #client.connect((adresseIP, port))
    print("Connecté au serveur")
    print("Tapez FIN pour terminer la conversation. ")
    session = """input("Veuillez-entrer la clef de session : ")"""
    #client.send(session.encode("utf-8"))
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                running = False
                continue
        pygame.draw.rect(Screen, (0, 0, 0), [0, 0, width, height])
        pygame.draw.line(Screen, (255, 255, 255), (width * 3 // 4, 0), (width * 3 // 4, height), 1)
        message = """input("> ")"""
        if message.lower() == "fin":
            running = False
        #client.send(message.encode("utf-8"))
        #reponse = client.recv(8191)
        #print(reponse.decode("utf-8"))
        pygame.display.flip()
        print(0)
    print("Connexion fermée")
except ConnectionRefusedError:
    print("erreur de connexion")

#client.close()
pygame.quit()
