from functools import wraps

from fastapi import HTTPException, status

from app.constants.enums import Role


forbidden_execption = HTTPException(
    status_code=status.HTTP_403_FORBIDDEN,
    detail="403 Access Denied: You do not have permissions to do this action",
)


def has_role(role: Role):
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            user = kwargs.get("current_user")
            if user is None or user.role != role:
                raise forbidden_execption
            return await func(*args, **kwargs)

        return wrapper
    return decorator


def is_owner_or_admin(func):
    @wraps(func)
    async def wrapper(*args, **kwargs):
        user_id = kwargs.get("user_id")
        user = kwargs.get("current_user")
        if user is None or (user.role != Role.ADMIN and user_id != user.id):
            raise forbidden_execption
        return await func(*args, **kwargs)

    return wrapper
