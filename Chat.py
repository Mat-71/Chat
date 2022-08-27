from datetime import datetime
from tkinter import *
from tkinter import ttk
from Client import Client

from ScrollableFrame import ScrollableFrame


class Interface:
    def __init__(self):
        self.client = None
        self.window = Tk()
        self.window.title("Chat")
        self.window.geometry("1920x1080")
        self.current_frame = None
        self.frames = {"connexion": self.connection_frame, "menu": self.menu_frame, "chat": self.chat_frame}

    def connection_frame(self):
        frame = Frame(self.window)
        Label(frame, text="Username:").grid(row=0)
        Label(frame, text="Password:").grid(row=1)
        username_input = Entry(frame)
        password_input = Entry(frame, show="*")
        username_input.grid(row=0, column=1)
        password_input.grid(row=1, column=1)
        login_button = Button(frame, text="Login",
                              command=lambda: self.connect_to_server(username_input.get(), password_input.get()))
        login_button.grid(row=3, column=0, sticky=W, pady=2)
        sign_up_button = Button(frame, text="Sign up",
                                command=lambda: self.connect_to_server(username_input.get(), password_input.get(),
                                                                       True))
        sign_up_button.grid(row=3, column=1, sticky=W, pady=4)
        return frame

    def menu_frame(self):
        self.client.get_friends()
        self.client.get_pending()
        self.client.get_requests()
        frame = Frame(self.window)
        log_out_button = Button(frame, text="Log out", command=self.log_out)
        log_out_button.pack()
        tabs = ttk.Notebook(frame)

        # "Chats" tab
        chats_tab = ttk.Frame(tabs)
        friends = list(self.client.keys.keys())
        print("friends:", friends)
        for i in range(len(friends)):
            friend = friends[i]
            button = Button(chats_tab, text=friend, command=lambda: self.switch_frame("chat", friend))
            button.grid(row=i, column=1, sticky=W, pady=2)
        tabs.add(chats_tab, text="Chats")

        # "Add friend" tab
        pending_tabs = ttk.Frame(tabs)
        i = 0
        for friend in self.client.pending:
            pending = Label(pending_tabs, text=friend)
            pending.grid(row=i, column=0, sticky=W, pady=2)
            i += 1
        new_friend = Entry(pending_tabs)
        new_friend.grid(row=0, column=1, sticky=W, pady=2)
        add_button = Button(pending_tabs, text="Add", command=lambda: self.send_request(new_friend.get()))
        add_button.grid(row=1, column=1, sticky=W, pady=2)
        tabs.add(pending_tabs, text="Add friend")

        # "See requests" tab
        requests_tab = ttk.Frame(tabs)
        i = 0
        for friend in self.client.requests:
            button = Button(requests_tab, text=friend, command=lambda: self.accept_friend(friend))
            button.grid(row=i, column=0, sticky=W, pady=2)
            i += 1
        tabs.add(requests_tab, text="See requests")

        tabs.pack(expand=1, fill=BOTH)
        return frame

    def chat_frame(self, friend: str = None):
        frame = Frame(self.window)

        menu_frame = Frame(frame)
        back_button = Button(menu_frame, text="Back", command=lambda: self.switch_frame("menu"))
        back_button.pack()
        menu_frame.place(relx=0, rely=0, relwidth=0.1)

        messages_frame = ScrollableFrame(frame, border=5, relief=SUNKEN)
        messages_frame.place(relx=0.1, rely=0, relwidth=0.9, relheight=0.9)

        for message in self.client.messages[friend]:
            text = Text(messages_frame.content, height=1, width=20)
            text.insert(END, Interface.format_message(message))
            text.pack(anchor=W if message["sender"] == friend else E)
            text.config(state=DISABLED)
            lines = len(text.get("1.0", "end").split("\n"))
            text.config(height=lines - 1)
        messages_frame.scroll_canvas()

        input_frame = Frame(frame)
        message_input = Entry(input_frame)
        message_input.focus()
        message_input.pack(fill=X, side=LEFT, expand=True)
        send_button = Button(input_frame, text="Send", command=lambda: self.send_message(message_input, friend))
        send_button.pack(fill=X, side=RIGHT)
        input_frame.place(relx=0.1, rely=0.9, relwidth=0.9, relheight=0.1)
        return frame

    def switch_frame(self, frame_name, *args):
        if self.current_frame is not None:
            self.current_frame.pack_forget()
        frame = None
        match frame_name:  # additional conditions and actions
            case "menu":
                if self.client is None or self.client.is_connected != 1:
                    frame = self.connection_frame()
            case "chat":
                self.client.get_messages()
        if frame is None:
            frame = self.frames[frame_name](*args)
        self.current_frame = frame
        frame.pack(expand=1, fill=BOTH)

    def connect_to_server(self, username: str, password: str, new=False):
        self.client = Client(username, password, new)
        if self.client.is_connected != 1:
            return
        self.switch_frame("menu")

    def log_out(self):
        self.client = None
        self.switch_frame("connexion")

    def send_message(self, message: Entry, friend: str):
        print(message.get())
        self.client.send_message(friend, message.get())
        message.delete(0, END)
        self.client.save()
        self.switch_frame("chat", friend)

    def send_request(self, friend: str):
        self.client.request_friend(friend)
        self.switch_frame("menu")

    def accept_friend(self, friend: str):
        self.client.accept_friend(friend)
        self.switch_frame("menu")

    @staticmethod
    def date_str(sent_time: int) -> str:
        date = datetime.fromtimestamp(sent_time // 1000)
        today = datetime.today()
        if date.year != today.year:
            return date.strftime("%a. %d %b. %Y, %H:%M")
        if date.month != today.month or date.day != today.day:
            return date.strftime("%a. %d %b., %H:%M")
        return date.strftime("%H:%M")

    @staticmethod
    def format_message(message: dict) -> str:
        sender, sent_time, content = message["sender"], message["sent_time"], message["content"]
        """
        if sent_by_user:
            return f"{content} : [{Interface.date_str(sent_time)}]"
        return f"{sender} [{Interface.date_str(sent_time)}]: {content}"
        """
        return content


if __name__ == "__main__":
    interface = Interface()
    interface.switch_frame("connexion")
    interface.window.mainloop()
    """
    username = "alice"
    password = "canada"
    username = "bob"
    password = "groenland"
    """
