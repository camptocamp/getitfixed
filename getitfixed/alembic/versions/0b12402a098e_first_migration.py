"""First migration

Revision ID: 0b12402a098e
Revises:
Create Date: 2020-05-20 16:47:03.128539

"""
from alembic import op
import sqlalchemy as sa
import geoalchemy2


# revision identifiers, used by Alembic.
revision = "0b12402a098e"
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        "category",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("label_fr", sa.String(length=50), nullable=True),
        sa.Column("label_en", sa.String(length=50), nullable=True),
        sa.Column("email", sa.String(length=50), nullable=False),
        sa.Column("icon", sa.String(length=150), nullable=True),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_category")),
        schema="getitfixed",
    )
    op.create_table(
        "type",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("label_fr", sa.String(length=50), nullable=True),
        sa.Column("label_en", sa.String(length=50), nullable=True),
        sa.Column("category_id", sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(
            ["category_id"],
            ["getitfixed.category.id"],
            name=op.f("fk_type_category_id_category"),
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_type")),
        schema="getitfixed",
    )
    op.create_table(
        "issue",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("hash", sa.Text(), nullable=False),
        sa.Column(
            "request_date", sa.Date(), server_default=sa.text("now()"), nullable=False
        ),
        sa.Column("type_id", sa.Integer(), nullable=False),
        sa.Column(
            "status",
            sa.Enum(
                "new",
                "validated",
                "in_progress",
                "waiting_for_reporter",
                "resolved",
                name="status",
                native_enum=False,
            ),
            nullable=False,
        ),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("localisation", sa.String(length=254), nullable=False),
        sa.Column(
            "geometry",
            geoalchemy2.types.Geometry(
                geometry_type="POINT", srid=4326, management=False
            ),
            nullable=True,
        ),
        sa.Column("firstname", sa.String(length=100), nullable=False),
        sa.Column("lastname", sa.String(length=100), nullable=False),
        sa.Column("phone", sa.String(length=20), nullable=False),
        sa.Column("email", sa.String(length=100), nullable=False),
        sa.ForeignKeyConstraint(
            ["type_id"], ["getitfixed.type.id"], name=op.f("fk_issue_type_id_type")
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_issue")),
        sa.UniqueConstraint("hash", name=op.f("uq_issue_hash")),
        schema="getitfixed",
    )
    op.create_table(
        "event",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("issue_id", sa.Integer(), nullable=False),
        sa.Column(
            "status",
            sa.Enum(
                "new",
                "validated",
                "in_progress",
                "waiting_for_reporter",
                "resolved",
                name="status",
                native_enum=False,
            ),
            nullable=False,
        ),
        sa.Column(
            "date",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column("comment", sa.Text(), nullable=True),
        sa.Column("private", sa.Boolean(), nullable=True),
        sa.Column(
            "author",
            sa.Enum("customer", "admin", name="author", native_enum=False),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["issue_id"], ["getitfixed.issue.id"], name=op.f("fk_event_issue_id_issue")
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_event")),
        schema="getitfixed",
    )
    op.create_table(
        "photo",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("filename", sa.Text(), nullable=True),
        sa.Column("data", sa.LargeBinary(), nullable=False),
        sa.Column("issue_id", sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(
            ["issue_id"], ["getitfixed.issue.id"], name=op.f("fk_photo_issue_id_issue")
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_photo")),
        schema="getitfixed",
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table("photo", schema="getitfixed")
    op.drop_table("event", schema="getitfixed")
    op.drop_table("issue", schema="getitfixed")
    op.drop_table("type", schema="getitfixed")
    op.drop_table("category", schema="getitfixed")
    # ### end Alembic commands ###
