"""create jobs table

Revision ID: 0001_create_jobs_table
Revises: 
Create Date: 2026-04-12
"""

from alembic import op
import sqlalchemy as sa

revision = "0001_create_jobs_table"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "jobs",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("original_url", sa.String(length=2048), nullable=False),
        sa.Column("canonical_url", sa.String(length=2048), nullable=False),
        sa.Column("canonical_url_hash", sa.String(length=64), nullable=False),
        sa.Column("company", sa.String(length=255), nullable=True),
        sa.Column("role", sa.String(length=255), nullable=True),
        sa.Column("source", sa.String(length=255), nullable=True),
        sa.Column("intake_method", sa.String(length=50), nullable=False),
        sa.Column("ingestion_status", sa.String(length=50), nullable=False),
        sa.Column("scrape_status", sa.String(length=50), nullable=False),
        sa.Column("analysis_status", sa.String(length=50), nullable=False),
        sa.Column("resume_status", sa.String(length=50), nullable=False),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_jobs_canonical_url_hash", "jobs", ["canonical_url_hash"], unique=True)


def downgrade() -> None:
    op.drop_index("ix_jobs_canonical_url_hash", table_name="jobs")
    op.drop_table("jobs")
