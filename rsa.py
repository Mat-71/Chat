from conversion import to_bytes, from_bytes


def encrypt(m: int, key: (int, int)) -> bytes:
    n, e = key
    c = pow(m, e, n)
    return to_bytes(c)


def decrypt(c: bytes, key: (int, int)) -> bytes:
    c = from_bytes(c, int)
    n, e = key
    m = pow(c, e, n)
    return m


if __name__ == "__main__":
    message = 69420
    print(message)
    result = encrypt(message, (2964324619, 65537))
    print(result)
    original = decrypt(result, (2964324619, 428098193))
    print(original)
