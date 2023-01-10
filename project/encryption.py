# Creating a Fernet Key to encrypt passwords. Key should be shifted to env variables later.
from cryptography.fernet import Fernet
from os import getenv

fernet_key = getenv("FERNET_KEY").encode()

fernet = Fernet(fernet_key)
