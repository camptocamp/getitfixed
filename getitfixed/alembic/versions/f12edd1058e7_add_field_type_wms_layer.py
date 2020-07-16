"""Add field type.wms_layer

Revision ID: f12edd1058e7
Revises: 0b12402a098e
Create Date: 2020-05-20 16:49:55.269463

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "f12edd1058e7"
down_revision = "0b12402a098e"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column(
        "type",
        sa.Column("wms_layer", sa.String(length=255), nullable=True),
        schema="getitfixed",
    )


def downgrade():
    op.drop_column("type", "wms_layer", schema="getitfixed")
