from sqlalchemy import ForeignKey, Integer, LargeBinary, String
from sqlalchemy.orm import Mapped, mapped_column

from src.infrastructure.db.base import Base


class PaymentModel(Base):
    __tablename__ = "transaction"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    amount: Mapped[int] = mapped_column(Integer)
    user_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        index=True,
    )
    account_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("account.id", ondelete="CASCADE"),
        index=True,
    )
    transaction_id: Mapped[str] = mapped_column(String, unique=True)
    signature: Mapped[bytes] = mapped_column(LargeBinary(32))
