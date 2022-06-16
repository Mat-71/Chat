import random

from primality_test import is_prime


def random_number(size: int) -> int:
    return random.randrange(2 ** (size - 1), 2 ** size - 1)


def generate_large_primes_with_password(password: str, keysize: int) -> (int, int):
    random.seed(password, 2)

    p = random_number(keysize)
    while not is_prime(p):
        p = random_number(keysize)
        if p % 2 == 0:
            p += 1

    q = random_number(keysize)
    while not is_prime(q) or p == q:
        q = random_number(keysize)
        if q % 2 == 0:
            q += 1
    return p, q


def inv_mod(e: int, phi: int) -> int:
    r1, r2 = e, phi
    u1, u2 = 1, 0
    v1, v2 = 0, 1
    while r2 != 0:
        q = r1 // r2
        r1, r2 = r2, r1 - q * r2
        u1, u2 = u2, u1 - q * u2
        v1, v2 = v2, v1 - q * v2
    return u1


def rsa_key_gen(p: int, q: int) -> ((int, int), (int, int)):
    n = p * q
    phi_n = (p - 1) * (q - 1)
    e = 65537
    d = inv_mod(e, phi_n)
    public_key = (n, e)
    private_key = (n, d)
    return public_key, private_key


def get_key_from_password(password: str, keysize: int = 2048) -> ((int, int), (int, int)):
    p, q = generate_large_primes_with_password(password, keysize)
    return rsa_key_gen(p, q)


if __name__ == "__main__":
    import time
    password = ""
    start = time.time()
    print(get_key_from_password(password))
    print(time.time() - start)
    start = time.time()
    print(get_key_from_password(password))
    print(time.time() - start)
