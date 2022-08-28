from Message import Message


class User:
    def __init__(self, username: str, pub_key: int, messages: list[dict[str, str | int]] = None,
                 keys: dict[str, tuple[int, int]] = None, requests: dict[str, int] = None,
                 pending: dict[str, int] = None, admin_level: int = 0):
        if messages is None:
            messages = []
        self.username = username
        self.pub_key = pub_key
        self.admin_level = admin_level
        self.messages = [Message(**message) for message in messages]
        # messages = [message, message, message]
        self.keys = dict[str, tuple[int, int]]() if keys is None else keys
        # key = {"username": (key_part_1, key_part_2)}
        self.requests = dict[str, int]() if requests is None else requests
        # requests = {"username": key}
        self.pending = dict[str, int]() if pending is None else pending
        # pending = {"username": key}

    @staticmethod
    def get_str_names(dict_names: dict[str]) -> str:
        return "|".join([f"{len(name)}|{name}" for name in dict_names.keys()])

    def get_friends(self) -> str:
        return User.get_str_names(self.keys)

    def get_aes_key(self, username: str) -> str:
        key_1, key_2 = self.keys[username]
        return f"{key_1}|{key_2}"

    def get_requests(self) -> str:
        return self.get_str_names(self.requests)

    def get_pending(self) -> str:
        return self.get_str_names(self.pending)

    def get_messages(self, n: int = 0) -> str:
        messages = self.messages[:n] if n else self.messages
        return "|".join([f"{len(str(message))}|{message}" for message in messages])

    def add_friend(self, friend: str, key: int):
        if friend in self.pending:
            key_part_1 = self.pending[friend]
            self.pending.pop(friend)
            key_part_2 = key
        else:
            key_part_1 = self.requests[friend]
            self.requests.pop(friend)
            key_part_2 = key
        self.keys[friend] = (key_part_1, key_part_2)

    def add_request(self, username: str, key: int):
        self.requests[username] = key

    def add_pending(self, username: str, key: int):
        self.pending[username] = key

    def new_message(self, content: str, username: str) -> str:
        message = Message(username, content)
        self.messages.append(message)
        return str(message.sent_time)

    def remove_message(self, sent_time: int):
        for message in self.messages:
            if message.sent_time == sent_time:
                self.messages.remove(message)
                return

    def __dict__(self) -> dict[str, str | int]:
        return {
            "username": self.username,
            "pub_key": self.pub_key,
            "messages": [message.__dict__() for message in self.messages],
            "keys": self.keys,
            "requests": self.requests,
            "pending": self.pending,
            "admin_level": self.admin_level
        }
