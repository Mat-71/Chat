import binascii


def encrypt(m: str, encrypt_key: (int, int)):
    m = int(binascii.hexlify(m.encode()), 16)
    if len(str(m)) < len(str(encrypt_key[0])):
        return pow(m, encrypt_key[1], encrypt_key[0])
    n = (len(str(m)) // len(str(encrypt_key[0]))) + 1
    m = list(str(m))
    for i in range(n - 1):
        m.insert((i + 1) * len(m) // n, "|")
    m = "".join(m).split("|")
    a = []
    for i in m:
        a.append(pow(int(i), encrypt_key[1], encrypt_key[0]))
    return a


def decrypt(m: int, decrypt_key: (int, int)):
    return pow(m, decrypt_key[1], decrypt_key[0])


def code(m, k: (int, int), mode):
    if mode == 1:
        a = ""
        if type(m) is str:
            return binascii.unhexlify(hex(decrypt(int(m), k))[2:]).decode()
        for i in m.split(','):
            a += decrypt(int(i), k)
        return binascii.unhexlify(hex(a)[2:]).decode()
    a = str(encrypt(m, k))
    return a.replace("[", "").replace("]", "").replace(" ", "")
