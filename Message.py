import time
import datetime


class Message:
    def __init__(self, username: str, content: str, sent_time: int = time.time() * 1000):
        self.username = username
        self.content = content
        self.sent_time = sent_time

    def __repr__(self):
        return f'{len(self.username)}|{self.sent_time}|{self.username}|{self.content}'

    def user_print(self) -> str:
        return f"{self.username} [{self.date_str()}]: {self.content}"

    def date_str(self) -> str:
        date = datetime.datetime.fromtimestamp(self.sent_time / 1000)
        today = datetime.datetime.today()
        if date.year != today.year:
            return date.strftime("%a. %d %b. %Y, %H:%M")
        if date.month != today.month or date.day != today.day:
            return date.strftime("%a. %d %b., %H:%M")
        return date.strftime("%H:%M")


if __name__ == "__main__":
    message1 = Message("redipac", "Hello world!")
    # message1.sent_time = datetime.datetime(year=2022, month=7, day=20, hour=17, minute=4).timestamp()
    print(message1)
    print(message1.user_print())
