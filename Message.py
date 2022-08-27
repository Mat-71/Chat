from time import time


class Message:
    def __init__(self, username: str, content: str, sent_time: int = None):
        if sent_time is None:
            sent_time = int(time() * 1000)
        self.username = username
        self.content = content
        self.sent_time = sent_time

    def __str__(self):
        return f'{self.sent_time}|{len(self.username)}|{self.username}|{self.content}'

    def __repr__(self):
        return str(self.__dict__)

    def __dict__(self):
        return {
            "username": self.username,
            "content": self.content,
            "sent_time": self.sent_time
        }


if __name__ == "__main__":
    message1 = Message("redipac", "Hello world!")
    # message1.sent_time = datetime.datetime(year=2022, month=7, day=20, hour=17, minute=4).timestamp()
    print(message1)
