# Creating a Fernet Key to encrypt passwords. Key should be shifted to env variables later.
from cryptography.fernet import Fernet


fernet_key = b'v__sKq22Hrm3BsoJz-WB6VmJrwHcwxLmYX2toWEL7aI='
fernet = Fernet(fernet_key)