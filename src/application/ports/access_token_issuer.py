from typing import Protocol


class AccessTokenIssuer(Protocol):
    def issue(self, user_id: int) -> str: ...
