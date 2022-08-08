def crypt(m: int, key: int | tuple[int, int]) -> int:
    match key:
        case int():
            n, e = key, 65537
        case (n, e):
            pass
        case _:
            raise TypeError(f"crypt | got {key} (type: {type(key).__name__} instead of int or tuple[int, int])")
    return pow(m, e, n)


if __name__ == "__main__":
    message = 69420
    print(message)
    result = crypt(message, 2964324619)
    print(result)
    original = crypt(result, (2964324619, 428098193))
    print(original)
