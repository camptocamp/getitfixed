"""Increase email fields length to 254 characters

Revision ID: 007ce1ec46f8
Revises: 2fdd37d28068
Create Date: 2021-03-03 09:11:59.993136

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "007ce1ec46f8"
down_revision = "2fdd37d28068"
branch_labels = None
depends_on = None


def upgrade():
    op.alter_column(
        "category", "email", type_=sa.VARCHAR(length=254), schema="getitfixed"
    )
    op.alter_column("issue", "email", type_=sa.VARCHAR(length=254), schema="getitfixed")


def downgrade():
    op.alter_column(
        "category", "email", type_=sa.VARCHAR(length=50), schema="getitfixed"
    )
    op.alter_column(
        "category", "email", type_=sa.VARCHAR(length=100), schema="getitfixed"
    )
