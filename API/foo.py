import bcrypt
from datetime import date


def get_hashed_password(plain_text_password):
    return bcrypt.hashpw(bytes(plain_text_password, encoding='utf8'), bcrypt.gensalt())


def check_password(plain_text_password, hashed_password):
    return bcrypt.checkpw(bytes(plain_text_password, encoding='utf8'), hashed_password)


def date_serializer(obj):
    if isinstance(obj, date):
        return obj.isoformat()  # Преобразует date в строку формата 'YYYY-MM-DD'
    raise TypeError(f"Type {obj.__class__.__name__} not serializable")
