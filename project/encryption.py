# Creating a Fernet Key to encrypt passwords. Key should be shifted to env variables later.
from os import getenv

from cryptography.fernet import Fernet

fernet_key = getenv("FERNET_KEY").encode()

fernet = Fernet(fernet_key)
