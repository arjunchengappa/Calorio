from project import db
from sqlalchemy.exc import IntegrityError
import logging


def transactional(function):
    def wrapper(*args, **kwargs):
        try:
            retval = function(*args, **kwargs)
            db.session.commit()
            return retval
        except IntegrityError as e:
            db.session.rollback()
            logging.error(e)
            raise e

    return wrapper
