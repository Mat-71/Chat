import random
from key_generator import get_key_from_password


def generate_salt(block_size: int) -> str:
    info_salt_size = len(bin(block_size // 2 - 1)) - 2
    _salt_size = random.randrange(pow(2, info_salt_size - 1), pow(2, info_salt_size))
    salt_size = str(bin(_salt_size))[2:]
    return salt_size + "".join([str(random.randrange(0, 2)) for _ in range(_salt_size)])


def encrypt_block(block: str, block_size: int, pub_key: (int, int)) -> str:
    n, e = pub_key
    m = int(block, 2)
    c = pow(m, e, n)
    cipher = ""
    for _ in range((block_size - 1) // 8 + 1):
        cipher = chr(c % 256) + cipher
        c //= 256
    return cipher


def encrypt(text: str, pub_key: (int, int)) -> str:
    n, _ = pub_key
    block_size = len(bin(n)) - 3
    bits = "".join([format(ord(c), '08b') for c in text])
    a = generate_salt(block_size)
    bits = a + bits
    while len(bits) % block_size != 0:
        bits = "0" + bits

    blocks = []
    curr_length = 0
    for bit in bits:
        if curr_length == block_size or curr_length == 0:
            blocks.append(bit)
            curr_length = 1
        else:
            blocks[-1] += bit
            curr_length += 1
    return "".join([encrypt_block(block, block_size, pub_key) for block in blocks])


def decrypt_block(block: str, block_size: int, priv_key: (int, int)) -> str:
    n, d = priv_key
    c = 0
    for i in block:
        c *= 256
        c += ord(i)
    m = pow(c, d, n)
    m = str(bin(m))[2:]
    while len(m) < block_size:
        m = "0" + m
    return m


def decrypt(cipher: str, priv_key: (int, int)) -> str:
    n, d = priv_key
    block_size = len(bin(n)) - 3
    blocks = []
    curr_length = 0
    for c in cipher:
        if curr_length == (block_size - 1) // 8 + 1 or curr_length == 0:
            blocks.append(c)
            curr_length = 1
        else:
            blocks[-1] += c
            curr_length += 1
    bits = ""
    for block in blocks:
        bits += decrypt_block(block, block_size, priv_key)
    while True:
        if bits[0] == "0":
            bits = bits[1:]
        else:
            break
    a = len(bin(block_size // 2 - 1)) - 2
    b = int(bits[:a], 2) + a
    bits = bits[b:]
    return "".join([chr(int(bits[i*8:i*8+8], 2)) for i in range(len(bits)//8)])


if __name__ == "__main__":
    result = encrypt("hello world", (221, 65537))
    original = decrypt(result, (221, 65))
    print(original)
