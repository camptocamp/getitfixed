"""Remove notnull on some fields

Revision ID: 2fdd37d28068
Revises: c58f6490f52e
Create Date: 2021-02-08 10:03:58.005431

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "2fdd37d28068"
down_revision = "c58f6490f52e"
branch_labels = None
depends_on = None


def upgrade():
    op.alter_column(
        "issue",
        "firstname",
        existing_type=sa.VARCHAR(length=100),
        nullable=True,
        schema="getitfixed",
    )
    op.alter_column(
        "issue",
        "lastname",
        existing_type=sa.VARCHAR(length=100),
        nullable=True,
        schema="getitfixed",
    )
    op.alter_column(
        "issue",
        "phone",
        existing_type=sa.VARCHAR(length=20),
        nullable=True,
        schema="getitfixed",
    )


def downgrade():
    op.alter_column(
        "issue",
        "phone",
        existing_type=sa.VARCHAR(length=20),
        nullable=False,
        schema="getitfixed",
    )
    op.alter_column(
        "issue",
        "lastname",
        existing_type=sa.VARCHAR(length=100),
        nullable=False,
        schema="getitfixed",
    )
    op.alter_column(
        "issue",
        "firstname",
        existing_type=sa.VARCHAR(length=100),
        nullable=False,
        schema="getitfixed",
    )
