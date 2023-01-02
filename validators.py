import re
from models import User
from encryption import fernet


def validate_password(password):
    if re.fullmatch(r'[A-Za-z0-9@#$%^&+=]{8,}', password):
        return True
    else:
        return False

def validate_user(email, password, is_encrypted=True):
    """
    Checks if a user with given email and password exists in the database. If is-encrypted
    is set to True, decrypts the given password before checking.
    """
    if is_encrypted:
        password = fernet.decrypt(password).decode()
    
    user = User.query.filter_by(email=email, password=password).first()
    return user