import time

from Message import Message


class User:
    def __init__(self, username: str, pub_key: int, messages: list = None, friends: list = None, requests: iter = None,
                 pendings=None):
        if messages is None:
            messages = []
        if friends is None:
            friends = {}
        if requests is None:
            requests = []
        if pendings is None:
            pendings = []
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
        self.friends = friends
        """
        {"bob": [(key, expiration, [m1, m2, m3]), (key, expiration, [m1, m2, m3])],
         "alice": [(key, expiration, [m1, m2, m3]), (key, expiration, [m1, m2, m3]), (key, expiration, [m1])]}
        """
        self.requests = requests
        self.pendings = pendings

    def __repr__(self):
        return str(self.__dict__())

    def get_friends(self):
        return "|".join([f"{len(name)},{name}" for name in self.friends.keys()])

    def get_requests(self):
        return "|".join([f"{len(name)},{name}" for name in self.requests])

    def get_pendings(self):
        return "|".join([f"{len(name)},{name}" for name in self.pendings])

    def add_friend(self, friend):
        self.friends[friend] = []
        if friend in self.requests:
            self.requests.remove(friend)
        if friend in self.pendings:
            self.pendings.remove(friend)

    def add_aes_key(self, friend, key):
        t = int(time.time())
        for _, expiration, _ in self.friends[friend]:
            if expiration >= t:
                return
        self.friends[friend].append((key, int(time.time() + 24 * 60 * 60), []))

    def add_request(self, request):
        self.requests.add(request)

    def add_pending(self, pending):
        self.pendings.add(pending)

    def new_message(self, _message, _username):
        for key, expiration, messages in self.friends[_username]:
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
            "friends": self.friends,
            "requests": self.requests,
            "pendings": self.pendings,
            "messages": [message.__dict__ for message in self.messages]
        }

