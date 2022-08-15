import tkinter as tk
from Client import Client
from key_generator import get_key_from_password


class Interface:
    def __init__(self):
        self.password = None
        self.username = None
        self.user = None
        self.window = tk.Tk()
        self.message = None

    def connexion_screen(self):
        tk.Label(self.window, text="username:").grid(row=0)
        tk.Label(self.window, text="Password:").grid(row=1)
        self.username = tk.Entry(self.window)
        self.password = tk.Entry(self.window)
        self.username.grid(row=0, column=1)
        self.password.grid(row=1, column=1)
        tk.Button(self.window, text="Login", command=self.login).grid(row=3, column=0, sticky=tk.W, pady=2)
        tk.Button(self.window, text="sign up", command=self.sign_up).grid(row=3, column=1, sticky=tk.W, pady=4)
        self.window.mainloop()

    def menu_screen(self):
        print("menu")
        if not isinstance(self.user, Client):
            self.connexion_screen()
        if self.user.is_connected != 1:
            self.connexion_screen()
        self.window.destroy()
        self.window = tk.Tk()
        self.user.get_friends()
        for i in self.user.keys:
            tk.Button(self.window, text=i, command=lambda m=i: self.conv(i)).grid(row=0, column=0, sticky=tk.W,
                                                                                  pady=2)
        self.window.mainloop()

    def conv(self, friend):

        if not isinstance(self.user, Client):
            self.connexion_screen()
        if self.user.is_connected != 1:
            self.connexion_screen()
        self.user.get_messages()
        self.window.destroy()
        self.window = tk.Tk()
        self.message = tk.Entry(self.window)
        self.message.grid(row=0, column=0, sticky=tk.W, pady=2)
        tk.Button(self.window, text="send", command=lambda m=self.message: self.send(m, friend)).grid(row=1, column=0, sticky=tk.W, pady=2)
        print(friend)

    def send(self, message, friend):
        print(message.get())
        self.user.send_message(friend, message.get())
        message.delete(0, tk.END)
        self.conv(friend)

    def login(self):
        print("username:", self.username.get())
        print("password:", self.password.get())
        public, private = get_key_from_password(self.username.get() + self.password.get())
        self.user = Client(self.username.get(), public, private)
        if self.user.is_connected != 1:
            print("login failed")
            self.connexion_screen()
            return
        print("login success")
        self.menu_screen()

    def sign_up(self):
        print("username:", self.username.get())
        print("password:", self.password.get())
        public, private = get_key_from_password(self.username.get() + self.password.get())
        self.user = Client(self.username.get(), public, private, True)
        if self.user.is_connected != 1:
            print("login failed")
            return
        print("login success")
        self.menu_screen()


interface = Interface()
interface.connexion_screen()
