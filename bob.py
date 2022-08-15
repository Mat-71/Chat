from Client import Client
from key_generator import get_key_from_password

username = "bob"
password = "groenland"
public, private = get_key_from_password(username + password)
bob = Client(username, public, private, True)
input()
bob.accept_friend('alice')


