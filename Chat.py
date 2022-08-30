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
        self.window.geometry("600x400")
        self.current_frame = None
        self.frames = {"connexion": self.connection_frame, "menu": self.menu_frame, "chat": self.chat_frame}

    def connection_frame(self):
        frame = Frame(self.window)
        connexion_frame = Frame(frame)
        Label(connexion_frame, text="Username:").grid(row=0)
        Label(connexion_frame, text="Password:").grid(row=1)
        username_input = Entry(connexion_frame)
        password_input = Entry(connexion_frame, show="*")
        username_input.grid(row=0, column=1)
        password_input.grid(row=1, column=1)
        login_button = Button(connexion_frame, text="Login",
                              command=lambda: self.connect_to_server(username_input.get(), password_input.get()))
        login_button.grid(row=3, column=0, sticky=W, pady=2)
        sign_up_button = Button(connexion_frame, text="Sign up",
                                command=lambda: self.connect_to_server(username_input.get(), password_input.get(),
                                                                       True))
        sign_up_button.grid(row=3, column=1, sticky=W, pady=4)
        connexion_frame.place(relx=0.4, rely=0.4, relwidth=1, relheight=1)
        return frame

    def menu_frame(self):
        self.client.get_friends()
        self.client.get_pending()
        self.client.get_requests()
        admin_level = self.client.get_admin_level()
        frame = Frame(self.window)
        tabs = ttk.Notebook(frame)
        tabs.place(x=0, y=0, relwidth=1, relheight=1)

        # "Log out" tab
        log_out_tab = ttk.Frame(tabs)
        tabs.add(log_out_tab, text="Log out")
        tabs.bind("<<NotebookTabChanged>>", lambda e: self.log_out() if tabs.index(CURRENT) == 0 else None)

        # "Chats" tab
        chats_tab = ttk.Frame(tabs)
        friends = list(self.client.keys.keys())
        print("friends:", friends)
        for i in range(len(friends)):
            friend = friends[i]
            button = Button(chats_tab, text=friend, command=lambda f=friend: self.switch_frame("chat", f))
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
            button = Button(requests_tab, text=friend, command=lambda f=friend: self.accept_friend(f))
            button.grid(row=i, column=0, sticky=W, pady=2)
            i += 1
        tabs.add(requests_tab, text="See requests")

        if admin_level > 0:
            # "Admin" tab
            admin_tab = ttk.Frame(tabs)

            # toggle frame
            toggle_frame = Frame(admin_tab, borderwidth=1, relief=SUNKEN)
            debug_toggle = IntVar()
            info_toggle = IntVar()
            warning_toggle = IntVar()
            error_toggle = IntVar()
            debug_toggle_button = Checkbutton(toggle_frame, text="Debug", variable=debug_toggle, onvalue=1, offvalue=0,
                                              height=1, width=20, anchor=W)
            info_toggle_button = Checkbutton(toggle_frame, text="Info", variable=info_toggle, onvalue=1, offvalue=0,
                                             height=1, width=20, anchor=W)
            warning_toggle_button = Checkbutton(toggle_frame, text="Warning", variable=warning_toggle, onvalue=1,
                                                offvalue=0, height=1, width=20, anchor=W)
            error_toggle_button = Checkbutton(toggle_frame, text="Error", variable=error_toggle, onvalue=1, offvalue=0,
                                              height=1, width=20, anchor=W)
            debug_toggle_button.grid(row=0, column=0, sticky=W, pady=2)
            info_toggle_button.grid(row=1, column=0, sticky=W, pady=2)
            warning_toggle_button.grid(row=2, column=0, sticky=W, pady=2)
            error_toggle_button.grid(row=3, column=0, sticky=W, pady=2)
            toggle_frame.place(relx=0, rely=0, relwidth=0.3, relheight=0.4)

            # logs frame
            logs_frame = Frame(admin_tab, borderwidth=1, relief=SUNKEN)
            logs = Text(logs_frame, wrap=WORD)
            logs.pack(fill=BOTH, expand=1)
            logs_frame.place(relx=0.3, rely=0, relwidth=0.7, relheight=0.9)

            # clients frame
            clients_frame = Frame(admin_tab, borderwidth=1, relief=SUNKEN)
            clients = Text(clients_frame, wrap=WORD)
            clients.pack(fill=BOTH, expand=1)
            clients_frame.place(relx=0, rely=0.4, relwidth=0.3, relheight=0.6)

            # command frame
            command_frame = Frame(admin_tab, borderwidth=1, relief=SUNKEN)
            command = Entry(command_frame)
            command.pack(fill=BOTH, expand=1)
            command.bind("<Return>", lambda e: (self.send_command(command.get()), command.delete(0, END)))
            command_frame.place(relx=0.3, rely=0.9, relwidth=0.7, relheight=0.1)

            tabs.add(admin_tab, text="Admin")

        tabs.select(1)
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
                self.client.save()
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
        self.client.log_out()
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

    def send_command(self, command: str):
        print("command:", command)
        self.client.send_aes(f"command|{command}")


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
