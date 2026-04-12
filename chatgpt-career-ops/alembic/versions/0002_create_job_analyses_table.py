"""create job analyses table

Revision ID: 0002_create_job_analyses_table
Revises: 0001_create_jobs_table
Create Date: 2026-04-12
"""

from alembic import op
import sqlalchemy as sa

revision = "0002_create_job_analyses_table"
down_revision = "0001_create_jobs_table"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "job_analyses",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("job_id", sa.Integer(), nullable=False),
        sa.Column("summary", sa.Text(), nullable=False),
        sa.Column("responsibilities", sa.JSON(), nullable=False),
        sa.Column("required_qualifications", sa.JSON(), nullable=False),
        sa.Column("preferred_qualifications", sa.JSON(), nullable=False),
        sa.Column("technical_skills", sa.JSON(), nullable=False),
        sa.Column("keywords", sa.JSON(), nullable=False),
        sa.Column("domain_signals", sa.JSON(), nullable=False),
        sa.Column("seniority_signals", sa.JSON(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["job_id"], ["jobs.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_job_analyses_job_id", "job_analyses", ["job_id"], unique=True)


def downgrade() -> None:
    op.drop_index("ix_job_analyses_job_id", table_name="job_analyses")
    op.drop_table("job_analyses")
