import random
import base64
from cryptography.fernet import Fernet
from os import path, getcwd

from Conversion import to_bytes, from_bytes


def get_fernet(key: int):
    random.seed(key)
    key = random.randbytes(32)
    key = base64.b64encode(key)
    fernet = Fernet(key)
    return fernet


def encrypt_file(username: str, key: int, content: str) -> tuple[str, bytes]:
    fernet = get_fernet(key)
    file_name = str(from_bytes(to_bytes(username), int))
    encrypted = fernet.encrypt(to_bytes(content))
    return file_name, encrypted


def decrypt_file(username: str, key: int) -> str | None:
    fernet = get_fernet(key)
    file_name = str(from_bytes(to_bytes(username), int))
    file_path = path.join(getcwd(), "Saves", file_name)
    if not path.exists(file_path):
        return None
    with open(file_path, 'rb') as file:
        encrypted = file.read()
    content = fernet.decrypt(encrypted)
    return from_bytes(content, str)
