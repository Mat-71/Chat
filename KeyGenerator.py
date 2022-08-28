from math import log, gcd
from random import seed as rand_seed, randrange, getrandbits

from MillerRabin import is_prime


def inv_mod(e: int, phi: int) -> int:
    r1, r2 = e, phi
    u1, u2 = 1, 0
    v1, v2 = 0, 1
    while r2 != 0:
        q = r1 // r2
        r1, r2 = r2, r1 - q * r2
        u1, u2 = u2, u1 - q * u2
        v1, v2 = v2, v1 - q * v2
    return u1 % phi


def rsa_key_gen(primes: tuple[int, int]) -> tuple[int, tuple[int, int]]:
    p, q = primes
    n = p * q
    phi_n = (p - 1) * (q - 1)
    e = 65537
    d = inv_mod(e, phi_n)
    public_key = n
    private_key = (n, d)
    return public_key, private_key


def random_number(size: int, seeded=False) -> int:
    if not seeded:
        rand_seed()
    return randrange(2 ** (size - 1), 2 ** size - 1)


def generate_prime(keysize: int) -> int:
    p = random_number(keysize, True)
    if p % 2 == 0:
        p += 1
    ln = log(p)
    prob = (ln - 1) / (ln ** 2)
    min_increment = int(1 / prob)
    min_increment += min_increment % 2
    increment = randrange(min_increment, 2 * min_increment, 2)
    while gcd(p, increment) > 1:
        p += 2
    print("increment:", increment)
    tries = 0
    while not is_prime(p):
        p += increment
        tries += 1
    print("tries:", tries)
    return p


def generate_large_primes_with_password(seed: int, keysize: int) -> tuple[int, int]:
    rand_seed(seed, 2)
    return generate_prime(keysize), generate_prime(keysize)


def get_key_from_password(username: str, password: str, keysize: int = 2048) -> tuple[int, tuple[int, int]]:
    if not isinstance(username, str):
        raise TypeError(f"get_key_from_password | got {username} (type: {type(username).__name__} instead of str)")
    if not isinstance(password, str):
        raise TypeError(f"get_key_from_password | got {password} (type: {type(password).__name__} instead of str)")
    rand_seed(username)
    _seed = getrandbits(256)
    rand_seed(password)
    _seed ^= getrandbits(256)
    return rsa_key_gen(generate_large_primes_with_password(_seed, keysize))


if __name__ == "__main__":
    import time

    start = time.time()
    print(get_key_from_password("Alice", "canada", 2048)[0])
    print(time.time() - start)
