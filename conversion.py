import math


def str_to_bytes(data: str) -> bytes:
    return data.encode('utf-8')


def int_to_bytes(data: int) -> bytes:
    return data.to_bytes(int(1 + math.log(data, 256)), 'big')


def float_to_bytes(data: float) -> bytes:
    return str_to_bytes(str(data))


def to_bytes(data) -> bytes:
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
    return data.decode('utf-8')


def bytes_to_int(data: bytes) -> int:
    return int.from_bytes(data, 'big')


def bytes_to_float(data: bytes) -> float:
    return float(bytes_to_str(data))


def from_bytes(data: bytes, target_type: type) -> any:
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
            raise Exception(f"Unable to convert '{type(data).__name__}' to 'bytes'")


if __name__ == "__main__":
    print(to_bytes(5))
    print(from_bytes(to_bytes(5), int))

    print(to_bytes(b"5"))
    print(from_bytes(to_bytes(b"5"), bytes))

    print(to_bytes("5"))
    print(from_bytes(to_bytes("5"), str))
