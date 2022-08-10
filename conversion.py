def str_to_bytes(data: str) -> bytes:
    return bytes([ord(c) for c in data])


def int_to_bytes(data: int) -> bytes:
    r = b""
    while data > 0:
        r = bytes([data % 256]) + r
        data //= 256
    return r


def float_to_bytes(data: float) -> bytes:
    return str_to_bytes(str(data))


def to_bytes(data: bytes | str | int | float) -> bytes:
    match data:
        case bytes():
            return data
        case str():
            return str_to_bytes(data)
        case int():
            return int_to_bytes(data)
        case float():
            return float_to_bytes(data)
        case _:
            raise Exception(f"Unable to convert '{type(data).__name__}' to 'bytes'")


def bytes_to_str(data: bytes) -> str:
    return "".join(map(lambda c: chr(int(c)), data))


def bytes_to_int(data: bytes) -> int:
    r = 0
    for b in data:
        r = r * 256 + int(b)
    return r


def bytes_to_float(data: bytes) -> float:
    return float(bytes_to_str(data))


def from_bytes(data: bytes, target_type: type) -> bytes | str | int | float:
    match target_type.__name__:
        case "bytes":
            return data
        case "str":
            return bytes_to_str(data)
        case "int":
            return bytes_to_int(data)
        case "float":
            return bytes_to_float(data)
        case _:
            raise Exception(f"Unable to convert 'bytes' to '{target_type.__name__}'")


if __name__ == "__main__":
    print(to_bytes(5))
    print(from_bytes(to_bytes(5), int))

    print(to_bytes(b"5"))
    print(from_bytes(to_bytes(b"5"), bytes))

    print(to_bytes("5"))
    print(from_bytes(to_bytes("5"), str))
