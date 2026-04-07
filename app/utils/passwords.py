import bcrypt


_STR_ENCODING = "utf-8"


def make_password(raw_password):
    byte_password = raw_password.encode(_STR_ENCODING)
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(byte_password, salt).decode(_STR_ENCODING)


def compare_passwords(raw_password, hashed_password):
    return bcrypt.checkpw(
        raw_password.encode(_STR_ENCODING),
        hashed_password.encode(_STR_ENCODING)
    )
