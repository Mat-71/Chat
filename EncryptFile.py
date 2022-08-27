import random
import base64
from cryptography.fernet import Fernet
import os

from Conversion import to_bytes, from_bytes

from Client import Client


def get_fernet(client: Client):
    random.seed(client.private_key[1])
    key = random.randbytes(32)
    key = base64.b64encode(key)
    fernet = Fernet(key)
    return fernet


def encrypt_file(client: Client, content: str):
    fernet = get_fernet(client)
    file_name = str(from_bytes(to_bytes(client.username), int))
    encrypted = fernet.encrypt(to_bytes(content))
    with open(file_name, 'wb') as file:
        file.write(encrypted)


def decrypt_file(client: Client) -> str | None:
    fernet = get_fernet(client)
    file_name = str(from_bytes(to_bytes(client.username), int))
    if not os.path.exists(file_name):
        return None
    with open(file_name, 'rb') as file:
        encrypted = file.read()
    content = fernet.decrypt(encrypted)
    return from_bytes(content, str)


if __name__ == '__main__':
    alice = Client('alice', 'canada')

