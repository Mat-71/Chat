def encrypt(m: int, key: (int, int)) -> int:
    n, e = key
    return pow(m, e, n)


def decrypt(c: int, key: (int, int)) -> bytes:
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
