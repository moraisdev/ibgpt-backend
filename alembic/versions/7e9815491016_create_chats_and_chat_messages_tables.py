"""create chats and chat_messages tables

Revision ID: 7e9815491016
Revises: 694a3b379ded
Create Date: 2024-12-25 21:45:54.722014

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "7e9815491016"
down_revision: Union[str, None] = "694a3b379ded"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "chats",
        sa.Column("id", sa.Integer(), primary_key=True, index=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("summary", sa.String(), nullable=True),
        sa.Column(
            "created_at",
            sa.TIMESTAMP(timezone=True),
            server_default=sa.text("timezone('America/Sao_Paulo', now())"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.TIMESTAMP(timezone=True),
            server_default=sa.text("timezone('America/Sao_Paulo', now())"),
            nullable=False,
        ),
    )

    op.create_table(
        "chat_messages",
        sa.Column("id", sa.Integer(), primary_key=True, index=True),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("role", sa.String(50), nullable=False),
        sa.Column("chat_id", sa.Integer(), sa.ForeignKey("chats.id"), nullable=False),
        sa.Column(
            "created_at",
            sa.TIMESTAMP(timezone=True),
            server_default=sa.text("timezone('America/Sao_Paulo', now())"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.TIMESTAMP(timezone=True),
            server_default=sa.text("timezone('America/Sao_Paulo', now())"),
            nullable=False,
        ),
    )


def downgrade() -> None:
    op.drop_table("chat_messages")
    op.drop_table("chats")
