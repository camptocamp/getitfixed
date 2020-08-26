"""Add field photo.hash

Revision ID: 73e05f3650a7
Revises: 6d8c64186efa
Create Date: 2020-07-24 09:05:07.981495

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "73e05f3650a7"
down_revision = "6d8c64186efa"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column(
        "photo",
        sa.Column("hash", sa.Text(), nullable=True, unique=True),
        schema="getitfixed",
    )
    op.execute(
        sa.text(
            "UPDATE getitfixed.photo"
            " SET hash = uuid_in(md5(random()::text || clock_timestamp()::text)::cstring);"
        )
    )
    op.alter_column("photo", "hash", nullable=False, schema="getitfixed")


def downgrade():
    op.drop_column("photo", "hash", schema="getitfixed")
