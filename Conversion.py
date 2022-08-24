class Conversion:
    @staticmethod
    def str_to_bytes(data: str) -> bytes:
        return bytes([ord(c) for c in data])

    @staticmethod
    def int_to_bytes(data: int) -> bytes:
        r = b""
        while data > 0:
            r = bytes([data % 256]) + r
            data //= 256
        return r

    @staticmethod
    def float_to_bytes(data: float) -> bytes:
        return Conversion.str_to_bytes(str(data))

    @staticmethod
    def to_bytes(data: bytes | str | int | float) -> bytes:
        match data:
            case bytes():
                return data
            case str():
                return Conversion.str_to_bytes(data)
            case int():
                return Conversion.int_to_bytes(data)
            case float():
                return Conversion.float_to_bytes(data)
            case _:
                raise Exception(f"Unable to convert '{type(data).__name__}' to 'bytes'")

    @staticmethod
    def bytes_to_str(data: bytes) -> str:
        return "".join(map(lambda c: chr(int(c)), data))

    @staticmethod
    def bytes_to_int(data: bytes) -> int:
        r = 0
        for b in data:
            r = r * 256 + int(b)
        return r

    @staticmethod
    def bytes_to_float(data: bytes) -> float:
        return float(Conversion.bytes_to_str(data))

    @staticmethod
    def from_bytes(data: bytes, target_type: type) -> bytes | str | int | float:
        match target_type.__name__:
            case "bytes":
                return data
            case "str":
                return Conversion.bytes_to_str(data)
            case "int":
                return Conversion.bytes_to_int(data)
            case "float":
                return Conversion.bytes_to_float(data)
            case _:
                raise Exception(f"Unable to convert 'bytes' to '{target_type.__name__}'")
