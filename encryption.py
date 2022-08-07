# THIS FILE IS UNUSED

import random


def generate_salt(block_size: int) -> str:
    info_salt_size = len(bin(block_size // 2 - 1)) - 2
    salt_size = random.randrange(block_size // 4, block_size // 2)
    # print(salt_size, base_size)
    info_salt = format(salt_size, f"0{info_salt_size}b")
    salt = "".join([str(random.randrange(0, 2)) for _ in range(salt_size - info_salt_size)])
    # print(f"info_salt_size: {info_salt_size}")
    # print(f"salt_size: {salt_size}")
    return info_salt + salt


def encrypt_block(block: str, block_size: int, pub_key: (int, int)) -> str:
    # print(block)
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
    # print(f"block_size: {block_size}")

    text += chr(3)
    bits = "".join([format(ord(c), '08b') for c in text])
    # print(f"bits:\n{bits}\n")

    salted_bits = generate_salt(block_size) + bits
    # print(f"salted_bits:\n{salted_bits}\n")

    blocks = []
    curr_length = 0
    for bit in salted_bits:
        if curr_length == block_size or curr_length == 0:
            blocks.append(bit)
            curr_length = 1
        else:
            blocks[-1] += bit
            curr_length += 1
    if len(blocks[-1]) < block_size:
        blocks[-1] += '0' * (block_size - len(blocks[-1]))
    return "".join([encrypt_block(block, block_size, pub_key) for block in blocks])


def decrypt_block(block: str, block_size: int, priv_key: (int, int)) -> str:
    n, d = priv_key
    c = 0
    for i in block:
        c *= 256
        c += ord(i)
    m = pow(c, d, n)
    # print(format(m, f"0{block_size}b"))
    return format(m, f"0{block_size}b")


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
    salted_bits = "".join([decrypt_block(block, block_size, priv_key) for block in blocks])
    # print(f"salted_bits:\n{salted_bits}\n")
    info_salt_size = len(bin(block_size // 2 - 1)) - 2
    salt_size = int(salted_bits[:info_salt_size], 2)
    # print(f"info_salt_size: {info_salt_size}")
    # print(f"salt_size: {salt_size}")
    bits = salted_bits[salt_size:]
    # print(f"bits:\n{bits}\n")
    # print([bits[i:i + 8] for i in range(0, len(bits), 8)])
    text = "".join([chr(int(c, 2)) for c in [bits[i:i + 8] for i in range(0, len(bits), 8)]])
    return text.rsplit(chr(3), 1)[0]


if __name__ == "__main__":
    message = "Hello world!"
    result = encrypt(message, (2964324619, 65537))
    print([ord(c) for c in result])
    original = decrypt(result, (2964324619, 428098193))
    print(original)
