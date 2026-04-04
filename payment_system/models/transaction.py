from sqlalchemy import ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base


class Transaction(Base):
    __tablename__ = "transaction"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    amount: Mapped[int] = mapped_column(Integer)
    user_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("user.id", ondelete="CASCADE"),
        index=True,
    )
    account_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("account.id", ondelete="CASCADE"),
        index=True,
    )
    transaction_id: Mapped[str] = mapped_column(String, unique=True)
