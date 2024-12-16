import bcrypt


def get_hashed_password(plain_text_password):
    return bcrypt.hashpw(bytes(plain_text_password, encoding='utf8'), bcrypt.gensalt())


def check_password(plain_text_password, hashed_password):
    return bcrypt.checkpw(bytes(plain_text_password, encoding='utf8'), hashed_password)
