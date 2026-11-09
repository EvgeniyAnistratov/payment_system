from dataclasses import dataclass

from src.domain.value_objects.role import Role


@dataclass(frozen=True, slots=True)
class AuthContext:
    user_id: int
    role: Role


@dataclass(frozen=True, slots=True)
class SignInInput:
    email: str
    password: str


@dataclass(frozen=True, slots=True)
class AccessTokenOutput:
    access_token: str
    token_type: str = "bearer"
