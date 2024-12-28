"""add subscription_status column to users

Revision ID: 694a3b379ded
Revises: 33216ba898b0
Create Date: 2024-12-25 18:12:18.261905

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "694a3b379ded"
down_revision: Union[str, None] = "33216ba898b0"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    op.add_column(
        "users",
        sa.Column(
            "subscription_status", sa.String(255), nullable=True, server_default=None
        ),
    )


def downgrade():
    op.drop_column("users", "subscription_status")
