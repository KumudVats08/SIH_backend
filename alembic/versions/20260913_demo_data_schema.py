"""Add districts, courses, and workforce skill availability.

Revision ID: 20260913_demo_data
Revises: 20260913_initial
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "20260913_demo_data"
down_revision: Union[str, None] = "20260913_initial"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "districts",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=100), nullable=False),
        sa.Column("target_learners", sa.Integer(), nullable=False),
        sa.Column("is_demo", sa.Boolean(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("name"),
    )
    op.create_index("ix_districts_id", "districts", ["id"], unique=False)
    op.create_index("ix_districts_name", "districts", ["name"], unique=True)

    op.create_table(
        "courses",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("description", sa.String(length=1000), nullable=True),
        sa.Column("district_id", sa.Integer(), nullable=True),
        sa.Column("is_demo", sa.Boolean(), nullable=False),
        sa.ForeignKeyConstraint(["district_id"], ["districts.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_courses_id", "courses", ["id"], unique=False)
    op.create_index("ix_courses_district_id", "courses", ["district_id"], unique=False)

    op.create_table(
        "course_skills",
        sa.Column("course_id", sa.Integer(), nullable=False),
        sa.Column("skill_id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(["course_id"], ["courses.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["skill_id"], ["skills.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("course_id", "skill_id"),
    )

    op.create_table(
        "workforce_skills",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("district_id", sa.Integer(), nullable=False),
        sa.Column("skill_id", sa.Integer(), nullable=False),
        sa.Column("available_count", sa.Integer(), nullable=False),
        sa.Column("is_demo", sa.Boolean(), nullable=False),
        sa.ForeignKeyConstraint(["district_id"], ["districts.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["skill_id"], ["skills.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("district_id", "skill_id"),
    )
    op.create_index("ix_workforce_skills_id", "workforce_skills", ["id"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_workforce_skills_id", table_name="workforce_skills")
    op.drop_table("workforce_skills")
    op.drop_table("course_skills")
    op.drop_index("ix_courses_district_id", table_name="courses")
    op.drop_index("ix_courses_id", table_name="courses")
    op.drop_table("courses")
    op.drop_index("ix_districts_name", table_name="districts")
    op.drop_index("ix_districts_id", table_name="districts")
    op.drop_table("districts")