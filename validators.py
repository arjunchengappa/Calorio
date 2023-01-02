import re

from encryption import fernet
from models import User


def validate_password(password):
    if re.fullmatch(r'[A-Za-z0-9@#$%^&+=]{8,}', password):
        return True
    else:
        return False
