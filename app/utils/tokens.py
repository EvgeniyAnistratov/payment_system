import datetime
import jwt

from app.core import settings


def get_access_token(user_id: int) -> str:
    exp = datetime.datetime.now(tz=datetime.timezone.utc) \
        + datetime.timedelta(minutes=settings.JWT_ACCESS_TTL)
    payload = {
        'exp': exp,
        'sub': str(user_id)
    }
    return jwt.encode(
        payload=payload,
        key=settings.JWT_SECRET_KEY,
        algorithm=settings.JWT_ALGORITHM
    )

def decode_token(token: str) -> dict | None:
    return jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
