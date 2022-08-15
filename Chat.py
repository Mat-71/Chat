import tkinter as tk
from Client import Client
from key_generator import get_key_from_password


class Interface:
    def __init__(self):
        self.client = None
        self.window = tk.Tk()
        self.window.title("Chat")
        self.window.geometry("300x300")
        self.current_frame = None
        self.frames = {"connexion": self.connexion_frame, "menu": self.menu_frame, "chat": self.chat_frame}

    def connexion_frame(self):
        frame = tk.Frame(self.window)
        username = tk.Entry(frame)
        password = tk.Entry(frame)
        username.grid(row=0, column=1)
        password.grid(row=1, column=1)
        login_button = tk.Button(frame, text="Login",
                                 command=lambda: self.connect_to_server(username.get(), password.get()))
        login_button.grid(row=3, column=0, sticky=tk.W, pady=2)
        sign_up_button = tk.Button(frame, text="Sign up",
                                   command=lambda: self.connect_to_server(username.get(), password.get(), True))
        sign_up_button.grid(row=3, column=1, sticky=tk.W, pady=4)
        return frame

    def menu_frame(self):
        self.client.get_friends()
        frame = tk.Frame(self.window)
        friends = list(self.client.keys.keys())
        print("friends:", friends)
        for i in range(len(friends)):
            friend = friends[i]
            button = tk.Button(frame, text=friend, command=lambda: self.switch_frame("chat", friend))
            button.grid(row=i, column=0, sticky=tk.W, pady=2)
        return frame

    def chat_frame(self, friend: str = None):
        frame = tk.Frame(self.window)
        message = tk.Entry(frame)
        message.grid(row=0, column=0, sticky=tk.W, pady=2)
        send_button = tk.Button(frame, text="Send", command=lambda m=message: self.send(m, friend))
        send_button.grid(row=1, column=0, sticky=tk.W, pady=2)
        back_button = tk.Button(frame, text="Back", command=lambda: self.switch_frame("menu"))
        back_button.grid(row=1, column=1, sticky=tk.W, pady=2)
        return frame

    def switch_frame(self, frame_name, *args):
        if self.current_frame is not None:
            self.current_frame.pack_forget()
        frame = None
        match frame_name:  # additional conditions and actions
            case "menu":
                if self.client is None or self.client.is_connected != 1:
                    frame = self.connexion_frame()
            case "chat":
                self.client.get_messages()
        if frame is None:
            frame = self.frames[frame_name](*args)
        frame.pack()
        self.current_frame = frame

    def connect_to_server(self, username: str, password: str, new=False):
        public, private = get_key_from_password(username + password)
        self.client = Client(username, public, private, new)
        if self.client.is_connected != 1:
            return
        self.switch_frame("menu")

    def send(self, message, friend: str):
        print(message.get())
        self.client.send_message(friend, message.get())
        message.delete(0, tk.END)
        self.switch_frame("chat", friend)


interface = Interface()
interface.switch_frame("connexion")
interface.window.mainloop()
