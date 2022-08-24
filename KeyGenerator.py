import math
import random

from primality_test import RabinMiller

is_prime = RabinMiller.is_prime


class KeyGenerator:
    @staticmethod
    def random_number(size: int, seeded=False) -> int:
        if not seeded:
            random.seed()
        return random.randrange(2 ** (size - 1), 2 ** size - 1)

    @staticmethod
    def generate_prime(keysize: int) -> int:
        p = KeyGenerator.random_number(keysize, True)
        if p % 2 == 0:
            p += 1
        ln = math.log(p)
        prob = 1 / ln - 1 / (ln ** 2)
        increment = random.randrange(int(p * prob), 2 * int(p * prob))
        increment += increment % 2
        while not is_prime(p):
            p += 2
        return p

    @staticmethod
    def generate_large_primes_with_password(seed: int, keysize: int) -> (int, int):
        random.seed(seed, 2)
        return KeyGenerator.generate_prime(keysize), KeyGenerator.generate_prime(keysize)

    @staticmethod
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

    @staticmethod
    def rsa_key_gen(primes: tuple[int, int]) -> (int, (int, int)):
        p, q = primes
        n = p * q
        phi_n = (p - 1) * (q - 1)
        e = 65537
        d = KeyGenerator.inv_mod(e, phi_n)
        public_key = n
        private_key = (n, d)
        return public_key, private_key

    @staticmethod
    def get_key_from_password(username: str, password: str, keysize: int = 2048) -> (int, (int, int)):
        if not isinstance(username, str):
            raise TypeError(f"get_key_from_password | got {username} (type: {type(username).__name__} instead of str)")
        if not isinstance(password, str):
            raise TypeError(f"get_key_from_password | got {password} (type: {type(password).__name__} instead of str)")
        random.seed(username)
        seed = random.getrandbits(256)
        random.seed(password)
        seed ^= random.getrandbits(256)
        return KeyGenerator.rsa_key_gen(KeyGenerator.generate_large_primes_with_password(seed, keysize))


if __name__ == "__main__":
    import time

    start = time.time()
    print(KeyGenerator.get_key_from_password("admin", "admin", 2048)[0])
    print(time.time() - start)
