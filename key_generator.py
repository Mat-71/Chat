import random

from primality_test import is_prime


def random_number(size: int) -> int:
    return random.randrange(2 ** (size - 1), 2 ** size - 1)


def generate_large_primes_with_password(seed: str, keysize: int) -> (int, int):
    random.seed(seed, 2)

    p = random_number(keysize)
    if p % 2 == 0:
        p += 1
    while not is_prime(p):
        p += 2

    q = random_number(keysize)
    if q % 2 == 0:
        q += 1
    while not is_prime(q) or p == q:
        q += 2
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


def rsa_key_gen(primes: tuple[int, int]) -> (int, (int, int)):
    p, q = primes
    n = p * q
    phi_n = (p - 1) * (q - 1)
    e = 65537
    d = inv_mod(e, phi_n)
    public_key = n
    private_key = (n, d)
    return public_key, private_key


def get_key_from_password(password: str, keysize: int = 2048) -> (int, (int, int)):
    if not isinstance(password, str):
        raise TypeError(f"get_key_from_password | got {password} (type: {type(password).__name__} instead of str)")
    return rsa_key_gen(generate_large_primes_with_password(password, keysize))


if __name__ == "__main__":
    import time

    start = time.time()
    print(get_key_from_password("azerty"))
    print(time.time() - start)
