"""Remove mandatory on issue.localisation

Revision ID: c58f6490f52e
Revises: 73e05f3650a7
Create Date: 2020-12-11 11:55:45.086901

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "c58f6490f52e"
down_revision = "73e05f3650a7"
branch_labels = None
depends_on = None


def upgrade():
    op.alter_column(
        "issue",
        "localisation",
        existing_type=sa.VARCHAR(length=254),
        nullable=True,
        schema="getitfixed",
    )


def downgrade():
    op.alter_column(
        "issue",
        "localisation",
        existing_type=sa.VARCHAR(length=254),
        nullable=False,
        schema="getitfixed",
    )
