from Client import Client
from key_generator import get_key_from_password

username = "bob"
password = "groenland"
public, private = get_key_from_password(username + password)
bob = Client(username, public, private)

input("3: get requests")
bob.get_requests()
print(bob.requests)

input("4: accept alice as friend")
bob.accept_friend("Alice")
input("6: get friends")
bob.get_friends()
print([username for username in bob.keys])
