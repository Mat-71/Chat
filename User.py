import time

from Message import Message


class User:
    def __init__(self, username: str, pub_key: int, messages: dict = None, keys: dict = None, requests: dict = None,
                 pendings: dict = None):
        if messages is None:
            messages = {}
        if keys is None:
            keys = {}
        if requests is None:
            requests = {}
        if pendings is None:
            pendings = {}
        self.username = username
        self.pub_key = pub_key
        self.messages = []
        for message in messages:
            match message:
                case Message():
                    self.messages.append(message)
                case dict():
                    self.messages.append(Message(**message))
                case _:
                    raise TypeError("Message must be a Message or a dict")
        """
        message = {"username": [message, message, message], "username": [message, message, message]}
        """
        self.keys = keys
        self.requests = requests
        self.pendings = pendings

    def __repr__(self):
        return str(self.__dict__())

    def get_friends(self):
        return "|".join([f"{len(name)},{name}" for name in self.keys])

    def get_requests(self):
        return "|".join([f"{len(name)},{name}" for name in self.requests])

    def get_pendings(self):
        return "|".join([f"{len(name)},{name}" for name in self.pendings])

    def add_friend(self, friend, key):
        self.keys[friend] = [key]
        if friend in self.requests:
            self.requests.remove(friend)
        if friend in self.pendings:
            self.keys[friend].append(self.pendings[friend])
            self.pendings.pop(friend, None)

    def add_request(self, request):
        self.requests.add(request)

    def add_pending(self, pending):
        self.pendings.add(pending)

    def new_message(self, _message, _username):
        for key, expiration, messages in self.keys[_username]:
            if expiration >= int(time.time()):
                messages.append(_message)
                return True
        self.messages.append(Message(_username, _message))

    def get_messages(self):
        return self.messages

    def __dict__(self):
        return {
            "username": self.username,
            "pub_key": self.pub_key,
            "friends": self.keys,
            "requests": self.requests,
            "pendings": self.pendings,
            "messages": [message.__dict__ for message in self.messages]
        }
