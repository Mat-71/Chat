import random


def generate_salt(block_size: int) -> str:
    salt_size = random.randrange(block_size // 4, block_size // 2)
    info_salt_size = len(bin(block_size // 2 - 1)) - 2
    return format(salt_size, f"0{info_salt_size}b") + "".join(
        [str(random.randrange(0, 2)) for _ in range(salt_size - info_salt_size)])


def encrypt_block(block: str, block_size: int, pub_key: (int, int)) -> str:
    print(block_size, block)
    n, e = pub_key
    m = int(block, 2)
    c = pow(m, e, n)
    cipher = ""
    for _ in range((block_size - 1) // 8 + 1):
        print(c % 256)
        cipher = chr(c % 256) + cipher
        c //= 256
    print(f"c: {c}")
    print(f"block length: {len(cipher)}")
    return cipher


def encrypt(text: str, pub_key: (int, int)) -> str:
    n, _ = pub_key
    block_size = len(bin(n)) - 3
    print(f"block_size: {block_size}")

    bits = "".join([format(ord(c), '08b') for c in text])

    bits = generate_salt(block_size) + bits
    print(f"bits: {bits}")

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


def decrypt_block(block: str, block_size: str, priv_key: (int, int)) -> str:
    n, d = priv_key
    c = 0
    for i in block:
        c *= 256
        c += ord(i)
    m = pow(c, d, n)
    print(c, m)
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
    for block in blocks:
        print(decrypt_block(block, block_size, priv_key))
    return cipher


if __name__ == "__main__":
    result = encrypt("hello world", (667, 3))
    print([ord(c) for c in result])
    original = decrypt(result, (667, 441))
