from sqlalchemy import Enum, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.domain.value_objects.role import Role
from src.infrastructure.db.base import Base
from src.infrastructure.db.models.account import AccountModel
from src.infrastructure.db.models.payment import PaymentModel


class UserModel(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    first_name: Mapped[str]
    surname: Mapped[str]
    last_name: Mapped[str | None]
    email: Mapped[str] = mapped_column(String(255), unique=True)
    password_hash: Mapped[str] = mapped_column(String)
    role: Mapped[Role] = mapped_column(
        Enum(Role, name="user_role_enum"),
        default=Role.USER,
        server_default=Role.USER.value,
    )

    accounts: Mapped[list[AccountModel]] = relationship(
        cascade="all, delete",
        passive_deletes=True,
    )
    payments: Mapped[list[PaymentModel]] = relationship(
        cascade="all, delete",
        passive_deletes=True,
    )
