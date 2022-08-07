# AES 256 encryption/decryption using pycryptodome library

import hashlib
from Cryptodome.Cipher import AES
from Cryptodome.Random import get_random_bytes


def encrypt(plain_text: str, password: bytes) -> bytes:
    # generate a random salt
    salt = get_random_bytes(AES.block_size)

    # use the Scrypt KDF to get a private key from the password
    private_key = hashlib.scrypt(
        password, salt=salt, n=2 ** 14, r=8, p=1, dklen=32)

    # create cipher config
    cipher_config = AES.new(private_key, AES.MODE_GCM)

    # return a dictionary with the encrypted text
    cipher_text, tag = cipher_config.encrypt_and_digest(bytes(plain_text, 'utf-8'))
    encrypted = cipher_text + salt + cipher_config.nonce + tag
    return encrypted


def decrypt(encrypted: bytes, password: bytes) -> str:
    cipher_text = encrypted[:-48]
    salt = encrypted[-48:-32]
    nonce = encrypted[-32:-16]
    tag = encrypted[-16:]

    # generate the private key from the password and salt
    private_key = hashlib.scrypt(
        password, salt=salt, n=2 ** 14, r=8, p=1, dklen=32)

    # create the cipher config
    cipher = AES.new(private_key, AES.MODE_GCM, nonce=nonce)

    # decrypt the cipher text
    decrypted = cipher.decrypt_and_verify(cipher_text, tag)

    return decrypted


if __name__ == "__main__":
    _password = b"admin"

    # First let us encrypt secret message
    _encrypted = encrypt("This is totally secret!!!vvvvvvveeeeeeeeerrrrrrrrrrryyyyyyyyyyy lllllllooooooooonnnnnnnnnnnnnnggggggggggggg", _password)
    print(_encrypted)

    # Let us decrypt using our original password
    _decrypted = decrypt(_encrypted, _password)
    print(bytes.decode(_decrypted))
