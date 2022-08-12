from Message import Message


class User:
    def __init__(self, username: str, pub_key: int, messages: list[dict[str, str | int]] = None,
                 keys: dict[str, tuple[int, int]] = None, requests: dict[str, int] = None,
                 pendings: dict[str, int] = None):
        if messages is None:
            messages = []
        if keys is None:
            keys: dict[str, tuple[int, int]] = {}
        if requests is None:
            requests: dict[str, int] = {}
        if pendings is None:
            pendings: dict[str, int] = {}
        self.username = username
        self.pub_key = pub_key
        self.messages = [Message(**message) for message in messages]  # messages = [message, message, message]
        self.keys = keys  # key = {"username": (key_part_1, key_part_2)}
        self.requests = requests  # requests = {"username": key}
        self.pendings = pendings  # pendings = {"username": key}

    def get_friends(self):
        return "|".join([f"{len(name)}|{name}|{self.keys[name]}" for name in self.keys])

    def get_aes_key(self, username: str) -> str:
        key_1, key_2 = self.keys[username]
        return f"{len(str(key_1))}{key_1}|{key_2}"

    def get_requests(self):
        return "|".join([f"{len(name)}|{name}" for name in self.requests])

    def get_pendings(self):
        return "|".join([f"{len(name)}|{name}" for name in self.pendings])

    def get_messages(self, n: int = 0) -> str:
        if n == 0:
            return "|".join([f"{len(str(message))}|{message}" for message in self.messages])
        return "|".join([f"{len(str(message))}|{message}" for message in self.messages[:n]])

    def add_friend(self, friend: str, key: int):
        if friend in self.pendings:
            key_part_1 = self.pendings[friend]
            self.pendings.pop(friend)
            key_part_2 = key
        else:
            key_part_2 = self.requests[friend]
            self.requests.pop(friend)
            key_part_1 = key
        self.keys[friend] = (key_part_1, key_part_2)

    def add_request(self, username: str, key: int):
        self.requests[username] = key

    def add_pending(self, username: str, key: int):
        self.pendings[username] = key

    def new_message(self, content: str, username: str) -> str:
        message = Message(username, content)
        self.messages.append(message)
        return str(message.sent_time)

    def remove_message(self, sent_time: int):
        for message in self.messages:
            if message.sent_time == sent_time:
                self.messages.remove(message)
                return


if __name__ == "__main__":
    _message = Message("redipac", "Hello world!")
    _user = User("redipac", 12345, [_message.__dict__, _message.__dict__], {"redipac": (42, 69)})
    print(_user.get_messages())
