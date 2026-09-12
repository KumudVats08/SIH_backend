import argparse
import csv
import re
import sys
from pathlib import Path

from dotenv import load_dotenv


project_root = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(Path(__file__).resolve().parent))
load_dotenv(project_root / ".env")

from database import SessionLocal
from models import Job, Skill


EXPERIENCE_PATTERN = re.compile(
    r"^(\d+)\s*-\s*(\d+)\s*(?:yr|yrs|year|years)$",
    re.IGNORECASE,
)


def clean(value: str | None) -> str | None:
    if value is None:
        return None
    value = value.strip()
    return value or None


def parse_experience(value: str | None) -> tuple[int | None, int | None]:
    match = EXPERIENCE_PATTERN.match(clean(value) or "")
    if not match:
        return None, None
    return int(match.group(1)), int(match.group(2))


def import_jobs(csv_path: Path) -> tuple[int, int]:
    session = SessionLocal()
    created = 0
    updated = 0
    jobs_by_id: dict[str, Job] = {}
    skills_by_name: dict[str, Skill] = {}

    try:
        with csv_path.open("r", encoding="utf-8-sig", newline="") as source:
            reader = csv.DictReader(source)
            for row_number, row in enumerate(reader, start=2):
                job_id = clean(row.get("job_id"))
                title = clean(row.get("job_title"))
                if not job_id or not title:
                    raise ValueError(f"Row {row_number} must contain job_id and job_title")

                minimum, maximum = parse_experience(row.get("experience_level"))
                job = jobs_by_id.get(job_id)
                if job is None:
                    job = session.query(Job).filter(Job.job_id == job_id).one_or_none()
                if job is None:
                    job = Job(job_id=job_id)
                    session.add(job)
                    created += 1
                elif job not in jobs_by_id.values():
                    updated += 1
                jobs_by_id[job_id] = job

                job.title = title
                job.company = clean(row.get("company"))
                job.platform = clean(row.get("platform"))
                job.location = clean(row.get("location"))
                job.employment_type = clean(row.get("employment_type"))
                job.sector = clean(row.get("sector"))
                job.job_url = clean(row.get("job_url"))
                job.experience_min = minimum
                job.experience_max = maximum

                skill_names = {
                    skill.strip().lower()
                    for skill in (clean(row.get("skills_required")) or "").split(",")
                    if skill.strip()
                }
                job.skills = []
                for skill_name in sorted(skill_names):
                    skill = skills_by_name.get(skill_name)
                    if skill is None:
                        skill = session.query(Skill).filter(Skill.name == skill_name).one_or_none()
                    if skill is None:
                        skill = Skill(name=skill_name)
                        session.add(skill)
                    skills_by_name[skill_name] = skill
                    job.skills.append(skill)

        session.commit()
        return created, updated
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


def main() -> None:
    parser = argparse.ArgumentParser(description="Import normalized job data into skill_gap_db")
    parser.add_argument("csv_path", type=Path, help="Path to the job CSV file")
    args = parser.parse_args()

    created, updated = import_jobs(args.csv_path)
    print(f"Imported jobs: {created} created, {updated} updated")


if __name__ == "__main__":
    main()