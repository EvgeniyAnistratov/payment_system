from src.domain.entities.user import User
from src.domain.value_objects.email import Email
from src.domain.value_objects.role import Role
from src.infrastructure.db.models.user import UserModel


class UserMapper:
    @staticmethod
    def to_domain(model: UserModel) -> User:
        role = model.role if isinstance(model.role, Role) else Role(model.role)
        return User(
            id=model.id,
            first_name=model.first_name,
            surname=model.surname,
            last_name=model.last_name,
            email=Email(model.email),
            password_hash=model.password_hash,
            role=role,
        )

    @staticmethod
    def to_persistence(entity: User) -> dict[str, object]:
        data: dict[str, object] = {
            "first_name": entity.first_name,
            "surname": entity.surname,
            "last_name": entity.last_name,
            "email": entity.email.value,
            "password_hash": entity.password_hash,
            "role": entity.role,
        }
        if entity.id is not None:
            data["id"] = entity.id
        return data
