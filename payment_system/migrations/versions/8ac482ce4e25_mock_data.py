"""Mock data

Revision ID: 8ac482ce4e25
Revises: e60e1e9e54f3
Create Date: 2026-04-05 19:19:44.394008

"""
from typing import Sequence, Union
from alembic import op
from payment_system.utils.passwords import make_password


# revision identifiers, used by Alembic.
revision: str = '8ac482ce4e25'
down_revision: Union[str, Sequence[str], None] = 'e60e1e9e54f3'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    sql_seq_updater = "SELECT setval(pg_get_serial_sequence('{0}', 'id'), (SELECT MAX(id) FROM {0}));"
    # users
    columns = "(id, first_name, surname, last_name, email, password_hash, role)"
    admin_password = make_password("admin_password")
    user_password = make_password("user_password")
    admin = f"1, 'Admin', 'user', NULL, 'admin@example.com', '{admin_password}', 'ADMIN'"
    user = f"2, 'Ivan', 'Ivanov', 'Ivanovich', 'ivan@example.com', '{user_password}', 'USER'"
    op.execute("INSERT INTO users {} VALUES ({}), ({})".format(columns, admin, user))
    op.execute(sql_seq_updater.format("users"))

    # accounts
    columns = "(id, balance, user_id)"
    account = "1, 50, 2"
    op.execute("INSERT INTO account {} VALUES ({})".format(columns, account))
    op.execute(sql_seq_updater.format("account"))


def downgrade() -> None:
    """Downgrade schema."""
    op.execute("DELETE FROM users WHERE id IN (1, 2)")
    op.execute("DELETE FROM account WHERE id=1")
