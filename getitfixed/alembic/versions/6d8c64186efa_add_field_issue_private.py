"""Add field issue.private

Revision ID: 6d8c64186efa
Revises: f12edd1058e7
Create Date: 2020-06-04 07:47:52.848957

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "6d8c64186efa"
down_revision = "f12edd1058e7"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column(
        "issue",
        sa.Column(
            "private", sa.Boolean(), nullable=False, server_default=sa.text("False")
        ),
        schema="getitfixed",
    )


def downgrade():
    op.drop_column("issue", "private", schema="getitfixed")
