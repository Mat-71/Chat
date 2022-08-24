# Credits to https://hackernoon.com/how-to-use-aes-256-cipher-python-cryptography-examples-6tbh37cr
# AES 256 encryption/decryption using pycryptodome library

import hashlib
from Cryptodome.Cipher import AES
from Cryptodome.Random import get_random_bytes

from Conversion import Conversion

from_bytes = Conversion.from_bytes
to_bytes = Conversion.to_bytes


class Aes:
    @staticmethod
    def encrypt(plain_text: str, password: int) -> bytes:
        # generate a random salt
        salt = get_random_bytes(AES.block_size)

        # use the Scrypt KDF to get a private key from the password
        private_key = hashlib.scrypt(to_bytes(password), salt=salt, n=2 ** 14, r=8, p=1, dklen=32)

        # create cipher config
        cipher_config = AES.new(private_key, AES.MODE_GCM)

        # return bytes of cipher text + salt + nonce + tag
        cipher_text, tag = cipher_config.encrypt_and_digest(bytes(plain_text, 'utf-8'))
        encrypted = cipher_text + salt + cipher_config.nonce + tag
        return encrypted

    @staticmethod
    def decrypt(encrypted: bytes, password: int) -> str:
        # get info from encrypted bytes
        cipher_text = encrypted[:-48]
        salt = encrypted[-48:-32]
        nonce = encrypted[-32:-16]
        tag = encrypted[-16:]

        # generate the private key from the password and salt
        private_key = hashlib.scrypt(to_bytes(password), salt=salt, n=2 ** 14, r=8, p=1, dklen=32)

        # create the cipher config
        cipher = AES.new(private_key, AES.MODE_GCM, nonce=nonce)

        # decrypt the cipher text
        decrypted = cipher.decrypt_and_verify(cipher_text, tag)

        return bytes.decode(decrypted)


if __name__ == "__main__":
    aes_key_s = from_bytes(b'\xba\xab\xba\xab\xba\xab\xba\xab\xba\xab\xba\xab\xba\xab\xba\xab', int)
    aes_key_bob = from_bytes(b'\xab\xab\xba\xab\xba\xab\xba\xab\xba\xab\xba\xab\xba\xab\xba\xab', int)
    username = "bob"
    content = "Hello Bob"

    bytes_encrypted = Aes.encrypt(content, aes_key_bob)
    str_encrypted = from_bytes(bytes_encrypted, str)
    print(f"Encrypted (bytes): {bytes_encrypted}")
    print(f"Encrypted (str): {str_encrypted}")
    print()
    message = f"message|{len(username)}|{username}|{str_encrypted}"
    encrypted_message = Aes.encrypt(message, aes_key_s)

    serveur_message = Aes.decrypt(encrypted_message, aes_key_s)
    action, username_length, data = serveur_message.split("|", 2)
    username = data[:int(username_length)]
    content = data[int(username_length) + 1:]
    print(f"action: {action}")
    print(f"username: {username}")
    print(f"content: {content}")
    print()

    bytes_encrypted = to_bytes(content)
    print(f"bytes_encrypted: {bytes_encrypted}")
    str_decrypted = Aes.decrypt(bytes_encrypted, aes_key_bob)
    print(f"decrypted: {str_decrypted}")