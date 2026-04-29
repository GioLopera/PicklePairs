"""initial schema

Revision ID: 001
Revises:
Create Date: 2026-04-16
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy import text
from sqlalchemy.dialects import postgresql
from sqlalchemy.exc import ProgrammingError

revision = "001"
down_revision = None
branch_labels = None
depends_on = None


def _create_enum_if_not_exists(name: str, *values: str) -> None:
    """Create a PostgreSQL enum type, skipping if it already exists."""
    bind = op.get_bind()
    result = bind.execute(
        text("SELECT 1 FROM pg_type WHERE typname = :name"),
        {"name": name}
    )
    if not result.fetchone():
        bind.execute(text(f"CREATE TYPE {name} AS ENUM ({', '.join(repr(v) for v in values)})"))


def upgrade() -> None:
    _create_enum_if_not_exists("room_status", "open", "closed")
    _create_enum_if_not_exists("assignment_status", "playing", "waiting")

    op.create_table(
        "rooms",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("room_code", sa.String(8), unique=True, nullable=False),
        sa.Column("name", sa.String(100), nullable=False),
        sa.Column("creator_token", sa.String(64), nullable=False),
        sa.Column("status", sa.Enum("open", "closed", name="room_status", create_type=False), nullable=False, server_default="open"),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column("closed_at", sa.DateTime(), nullable=True),
    )
    op.create_index("ix_rooms_room_code", "rooms", ["room_code"])

    op.create_table(
        "players",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("room_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("rooms.id"), nullable=False),
        sa.Column("name", sa.String(50), nullable=False),
        sa.Column("joined_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.UniqueConstraint("room_id", "name", name="uq_player_name_per_room"),
    )

    op.create_table(
        "team_results",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("room_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("rooms.id"), nullable=False),
        sa.Column("run_number", sa.Integer(), nullable=False),
        sa.Column("generated_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
    )

    op.create_table(
        "team_assignments",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("result_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("team_results.id"), nullable=False),
        sa.Column("player_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("players.id"), nullable=False),
        sa.Column("team_number", sa.Integer(), nullable=False),
        sa.Column(
            "status",
            sa.Enum("playing", "waiting", name="assignment_status", create_type=False),
            nullable=False,
            server_default="playing",
        ),
    )


def downgrade() -> None:
    op.drop_table("team_assignments")
    op.drop_table("team_results")
    op.drop_table("players")
    op.drop_table("rooms")
    bind = op.get_bind()
    bind.execute(text("DROP TYPE IF EXISTS assignment_status"))
    bind.execute(text("DROP TYPE IF EXISTS room_status"))
