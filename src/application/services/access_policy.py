from src.application.dtos.auth import AuthContext
from src.application.errors.access_denied import AccessDeniedError
from src.domain.value_objects.role import Role


def ensure_admin(actor: AuthContext) -> None:
    if actor.role is not Role.ADMIN:
        raise AccessDeniedError("You do not have permissions to do this action")


def ensure_owner_or_admin(actor: AuthContext, user_id: int) -> None:
    if actor.role is not Role.ADMIN and actor.user_id != user_id:
        raise AccessDeniedError("You do not have permissions to do this action")
