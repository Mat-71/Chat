import datetime
import tkinter as tk
from tkinter import ttk
from Client import Client
from ScrollableFrame import ScrollableFrame
from key_generator import get_key_from_password


class Interface:
    def __init__(self):
        self.client = None
        self.window = tk.Tk()
        self.window.title("Chat")
        self.window.geometry("1920x1080")
        self.current_frame = None
        self.frames = {"connexion": self.connection_frame, "menu": self.menu_frame, "chat": self.chat_frame}

    def connection_frame(self):
        frame = tk.Frame(self.window)
        tk.Label(frame, text="Username:").grid(row=0)
        tk.Label(frame, text="Password:").grid(row=1)
        username_input = tk.Entry(frame)
        password_input = tk.Entry(frame, show="*")
        username_input.grid(row=0, column=1)
        password_input.grid(row=1, column=1)
        login_button = tk.Button(frame, text="Login",
                                 command=lambda: self.connect_to_server(username_input.get(), password_input.get()))
        login_button.grid(row=3, column=0, sticky=tk.W, pady=2)
        sign_up_button = tk.Button(frame, text="Sign up",
                                   command=lambda: self.connect_to_server(username_input.get(), password_input.get(),
                                                                          True))
        sign_up_button.grid(row=3, column=1, sticky=tk.W, pady=4)
        return frame

    def menu_frame(self):
        self.client.get_friends()
        self.client.get_pending()
        self.client.get_requests()
        frame = tk.Frame(self.window)
        log_out_button = tk.Button(frame, text="Log out", command=self.log_out)
        log_out_button.pack()
        tabs = ttk.Notebook(frame)

        # "Chats" tab
        chats_tab = ttk.Frame(tabs)
        friends = list(self.client.keys.keys())
        print("friends:", friends)
        for i in range(len(friends)):
            friend = friends[i]
            button = tk.Button(chats_tab, text=friend, command=lambda: self.switch_frame("chat", friend))
            button.grid(row=i, column=1, sticky=tk.W, pady=2)
        tabs.add(chats_tab, text="Chats")

        # "Add friend" tab
        pending_tabs = ttk.Frame(tabs)
        i = 0
        for friend in self.client.pending:
            pending = tk.Label(pending_tabs, text=friend)
            pending.grid(row=i, column=0, sticky=tk.W, pady=2)
            i += 1
        new_friend = tk.Entry(pending_tabs)
        new_friend.grid(row=0, column=1, sticky=tk.W, pady=2)
        add_button = tk.Button(pending_tabs, text="Add", command=lambda: self.send_request(new_friend.get()))
        add_button.grid(row=1, column=1, sticky=tk.W, pady=2)
        tabs.add(pending_tabs, text="Add friend")

        # "See requests" tab
        requests_tab = ttk.Frame(tabs)
        i = 0
        for friend in self.client.requests:
            button = tk.Button(requests_tab, text=friend, command=lambda: self.accept_friend(friend))
            button.grid(row=i, column=0, sticky=tk.W, pady=2)
            i += 1
        tabs.add(requests_tab, text="See requests")

        tabs.pack(expand=1, fill=tk.BOTH)
        return frame

    def chat_frame(self, friend: str = None):
        frame = tk.Frame(self.window)

        menu_frame = tk.Frame(frame)
        back_button = tk.Button(menu_frame, text="Back", command=lambda: self.switch_frame("menu"))
        back_button.pack()
        menu_frame.place(relx=0, rely=0, relwidth=0.1)

        messages_frame = ScrollableFrame(frame, border=5, relief=tk.SUNKEN)
        messages_frame.place(relx=0.1, rely=0, relwidth=0.9, relheight=0.9)

        for message in self.client.messages[friend]:
            text = tk.Text(messages_frame.content, height=1, width=20)
            text.insert(tk.END, Interface.format_message(message))
            text.pack(anchor=tk.W if message["sender"] == friend else tk.E)
            text.config(state=tk.DISABLED)
            lines = len(text.get("1.0", "end").split("\n"))
            text.config(height=lines - 1)
        messages_frame.scroll_canvas()

        input_frame = tk.Frame(frame)
        message_input = tk.Entry(input_frame)
        message_input.focus()
        message_input.pack(fill=tk.X, side=tk.LEFT, expand=True)
        send_button = tk.Button(input_frame, text="Send", command=lambda: self.send_message(message_input, friend))
        send_button.pack(fill=tk.X, side=tk.RIGHT)
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
        frame.pack(expand=1, fill=tk.BOTH)

    def connect_to_server(self, username: str, password: str, new=False):
        public, private = get_key_from_password(username + password)
        self.client = Client(username, public, private, new)
        if self.client.is_connected != 1:
            return
        self.switch_frame("menu")

    def log_out(self):
        self.client = None
        self.switch_frame("connexion")

    def send_message(self, message: tk.Entry, friend: str):
        print(message.get())
        self.client.send_message(friend, message.get())
        message.delete(0, tk.END)
        self.switch_frame("chat", friend)

    def send_request(self, friend: str):
        self.client.request_friend(friend)
        self.switch_frame("menu")

    def accept_friend(self, friend: str):
        self.client.accept_friend(friend)
        self.switch_frame("menu")

    @staticmethod
    def date_str(sent_time: int) -> str:
        date = datetime.datetime.fromtimestamp(sent_time // 1000)
        today = datetime.datetime.today()
        if date.year != today.year:
            return date.strftime("%a. %d %b. %Y, %H:%M")
        if date.month != today.month or date.day != today.day:
            return date.strftime("%a. %d %b., %H:%M")
        return date.strftime("%H:%M")

    @staticmethod
    def format_message(message: dict, sent_by_user: bool = False) -> str:
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
