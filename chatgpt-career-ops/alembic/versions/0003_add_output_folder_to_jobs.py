"""add output folder to jobs

Revision ID: 0003_add_output_folder_to_jobs
Revises: 0002_create_job_analyses_table
Create Date: 2026-04-12
"""

from alembic import op
import sqlalchemy as sa

revision = "0003_add_output_folder_to_jobs"
down_revision = "0002_create_job_analyses_table"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("jobs", sa.Column("output_folder", sa.String(length=512), nullable=True))


def downgrade() -> None:
    op.drop_column("jobs", "output_folder")
