import hashlib


_ENCODING = "utf-8"


def _get_raw_string(payload: dict, secret: str) -> str:
    keys = list(payload.keys())
    keys.sort()

    parts = [str(payload.get(k)) for k in keys]
    parts.append(secret)

    return "".join(parts)


def check_singature(payload: dict, signature: str, secret: str) -> bool:
    return generate_signature(payload, secret) == signature


def generate_signature(payload: dict, secret: str) -> str:
    raw_string = _get_raw_string(payload, secret)
    return hashlib.sha256(raw_string.encode(_ENCODING)).hexdigest()
