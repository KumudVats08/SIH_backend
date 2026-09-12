"""Create the application and job-market tables.

Revision ID: 20260913_initial
Revises:
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "20260913_initial"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "employers",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("email", sa.String(length=255), nullable=False),
        sa.Column("password_hash", sa.String(length=255), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("email"),
    )
    op.create_index("ix_employers_id", "employers", ["id"], unique=False)
    op.create_index("ix_employers_email", "employers", ["email"], unique=True)

    op.create_table(
        "jobs",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("job_id", sa.String(length=50), nullable=False),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("company", sa.String(length=255), nullable=True),
        sa.Column("platform", sa.String(length=255), nullable=True),
        sa.Column("location", sa.String(length=255), nullable=True),
        sa.Column("employment_type", sa.String(length=50), nullable=True),
        sa.Column("sector", sa.String(length=100), nullable=True),
        sa.Column("job_url", sa.String(length=500), nullable=True),
        sa.Column("experience_min", sa.Integer(), nullable=True),
        sa.Column("experience_max", sa.Integer(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("job_id"),
    )
    op.create_index("ix_jobs_id", "jobs", ["id"], unique=False)
    op.create_index("ix_jobs_job_id", "jobs", ["job_id"], unique=True)
    op.create_index("ix_jobs_location", "jobs", ["location"], unique=False)
    op.create_index("ix_jobs_sector", "jobs", ["sector"], unique=False)

    op.create_table(
        "skills",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=100), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("name"),
    )
    op.create_index("ix_skills_id", "skills", ["id"], unique=False)
    op.create_index("ix_skills_name", "skills", ["name"], unique=True)

    op.create_table(
        "job_skills",
        sa.Column("job_id", sa.Integer(), nullable=False),
        sa.Column("skill_id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(["job_id"], ["jobs.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["skill_id"], ["skills.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("job_id", "skill_id"),
    )

    op.create_table(
        "gap_validations",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("gap_id", sa.Integer(), nullable=False),
        sa.Column("employer_id", sa.Integer(), nullable=False),
        sa.Column("decision", sa.String(length=20), nullable=False),
        sa.Column("comment", sa.String(length=1000), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["employer_id"], ["employers.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_gap_validations_id", "gap_validations", ["id"], unique=False)
    op.create_index("ix_gap_validations_gap_id", "gap_validations", ["gap_id"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_gap_validations_gap_id", table_name="gap_validations")
    op.drop_index("ix_gap_validations_id", table_name="gap_validations")
    op.drop_table("gap_validations")
    op.drop_table("job_skills")
    op.drop_index("ix_skills_name", table_name="skills")
    op.drop_index("ix_skills_id", table_name="skills")
    op.drop_table("skills")
    op.drop_index("ix_jobs_sector", table_name="jobs")
    op.drop_index("ix_jobs_location", table_name="jobs")
    op.drop_index("ix_jobs_job_id", table_name="jobs")
    op.drop_index("ix_jobs_id", table_name="jobs")
    op.drop_table("jobs")
    op.drop_index("ix_employers_email", table_name="employers")
    op.drop_index("ix_employers_id", table_name="employers")
    op.drop_table("employers")