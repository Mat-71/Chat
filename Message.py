import time
import datetime


class Message:
    def __init__(self, username: str, content: str):
        self.username = username
        self.content = content
        self.sent_time = int(time.time())

    def date_str(self) -> str:
        date = datetime.datetime.fromtimestamp(self.sent_time)
        today = datetime.datetime.today()
        if date.year != today.year:
            return date.strftime("%a. %d %b. %Y, %H:%M")
        if date.month != today.month or date.day != today.day:
            return date.strftime("%a. %d %b., %H:%M")
        return date.strftime("%H:%M")

    def __repr__(self) -> str:
        return f"{self.username} [{self.date_str()}]: {self.content}"

    def send_format(self) -> str:
        return f"{len(self.username)}|{self.username}|{self.sent_time}|{self.content}"


if __name__ == "__main__":
    message1 = Message("redipac", "Hello world!")
    # message1.sent_time = datetime.datetime(year=2022, month=7, day=20, hour=17, minute=4).timestamp()
    print(message1)
    print(message1.send_format())
