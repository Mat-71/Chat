import socket
import time

adresseIP = "172.16.1.69"  # Ici, le poste local
port = 12800  # Se connecter sur le port 50000

message = ""
try:
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect((adresseIP, port))
    client.send(b'|login|admin|f14da2c83f8f51380bfcc7c198e943ad')
    time.sleep(0.1)
    client.send(b'|shutdown')
    time.sleep(0.1)
except ConnectionRefusedError:
    pass
