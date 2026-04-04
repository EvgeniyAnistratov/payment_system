from sqlalchemy import Enum, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from payment_system.constants.enums import Role

from .base import Base


class User(Base):
    __tablename__ = "user"

    id: Mapped[int] = mapped_column(primary_key=True)
    first_name: Mapped[str]
    surname: Mapped[str]
    last_name: Mapped[str]
    email: Mapped[str] = mapped_column(String(255), unique=True)
    password_hash: Mapped[str] = mapped_column(String)
    role: Mapped[Role] = mapped_column(
        Enum(Role, name="user_role_enum"),
        default=Role.USER,
        server_default=Role.USER.value
    )

    accounts = relationship(
        "Account",
        cascade="all, delete",
        passive_deletes=True,
    )
    transactions = relationship(
        "Transaction",
        cascade="all, delete",
        passive_deletes=True,
    )

    @property
    def fullname(self):
        return f"{self.surname} {self.first_name} {self.last_name}"
