import random

from primality_test import is_prime


def random_number(size: int) -> int:
    return random.randrange(2 ** (size - 1), 2 ** size - 1)


def generate_large_prime_with_password(password: str, keysize: int = 2048) -> int:
    random.seed(password, 2)
    n = random_number(keysize)
    while not is_prime(n):
        n = random_number()
        if n % 2 == 0:
            n += 1
    return n
