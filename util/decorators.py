from project import db


def transactional(function):
    def wrapper(*args, **kwargs):
        try:
            retval = function(*args, **kwargs)
            db.session.commit()
            return retval
        except Exception as e:
            db.session.rollback()
            raise e
    return wrapper
