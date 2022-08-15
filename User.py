from Message import Message


class User:
    def __init__(self, username: str, pub_key: int, messages: list[dict[str, str | int]] = None,
                 keys: dict[str, tuple[int, int]] = None, requests: dict[str, int] = None,
                 pending: dict[str, int] = None):
        if messages is None:
            messages = []
        if keys is None:
            keys: dict[str, tuple[int, int]] = {}
        if requests is None:
            requests: dict[str, int] = {}
        if pending is None:
            pending: dict[str, int] = {}
        self.username = username
        self.pub_key = pub_key
        self.messages = [Message(**message) for message in messages]  # messages = [message, message, message]
        self.keys = keys  # key = {"username": (key_part_1, key_part_2)}
        self.requests = requests  # requests = {"username": key}
        self.pending = pending  # pending = {"username": key}

    def get_friends(self):
        return "|".join([f"{len(name)}|{name}|{self.keys[name]}" for name in self.keys])

    def get_aes_key(self, username: str) -> str:
        key_1, key_2 = self.keys[username]
        return f"{key_1}|{key_2}"

    def get_requests(self):
        return "|".join([f"{len(name)}|{name}" for name in self.requests])

    def get_pending(self):
        return "|".join([f"{len(name)}|{name}" for name in self.pending])

    def get_messages(self, n: int = 0) -> str:
        if n == 0:
            return "|".join([f"{len(str(message))}|{message}" for message in self.messages])
        return "|".join([f"{len(str(message))}|{message}" for message in self.messages[:n]])

    def add_friend(self, friend: str, key: int):
        if friend in self.pending:
            key_part_1 = self.pending[friend]
            self.pending.pop(friend)
            key_part_2 = key
        else:
            key_part_2 = self.requests[friend]
            self.requests.pop(friend)
            key_part_1 = key
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

    def __dict__(self):
        return {
            "username": self.username,
            "pub_key": self.pub_key,
            "messages": [message.__dict__() for message in self.messages],
            "keys": self.keys,
            "requests": self.requests,
            "pending": self.pending
        }
