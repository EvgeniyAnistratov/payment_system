"""Mock data

Revision ID: 8ac482ce4e25
Revises: e60e1e9e54f3
Create Date: 2026-04-05 19:19:44.394008

"""
from typing import Sequence, Union

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "8ac482ce4e25"
down_revision: Union[str, Sequence[str], None] = "e60e1e9e54f3"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

# bcrypt hashes of admin_password and user_password. Migrations must not import
# application code: the hasher can change, the seed data must not.
ADMIN_PASSWORD_HASH = "$2b$12$gPT/EwTd/f5p7dkGUa1HLOTCwcsOhh.BB.cEfXEE.5V7l2f6sPUc."
USER_PASSWORD_HASH = "$2b$12$L/0Y3HSMhi9Hbz88kDSoOuSWPENXyhMJsk6.xz9/w0B9x5p8BspmG"


def upgrade() -> None:
    """Upgrade schema."""
    sql_seq_updater = (
        "SELECT setval(pg_get_serial_sequence('{0}', 'id'), (SELECT MAX(id) FROM {0}));"
    )
    columns = "(id, first_name, surname, last_name, email, password_hash, role)"
    admin = (
        "1, 'Admin', 'user', NULL, 'admin@example.com', "
        f"'{ADMIN_PASSWORD_HASH}', 'ADMIN'"
    )
    user = (
        "2, 'Ivan', 'Ivanov', 'Ivanovich', 'ivan@example.com', "
        f"'{USER_PASSWORD_HASH}', 'USER'"
    )
    op.execute(f"INSERT INTO users {columns} VALUES ({admin}), ({user})")
    op.execute(sql_seq_updater.format("users"))

    columns = "(id, balance, user_id)"
    op.execute(f"INSERT INTO account {columns} VALUES (1, 50, 2)")
    op.execute(sql_seq_updater.format("account"))


def downgrade() -> None:
    """Downgrade schema."""
    op.execute("DELETE FROM users WHERE id IN (1, 2)")
    op.execute("DELETE FROM account WHERE id=1")
