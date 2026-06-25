from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.company import Company
from app.models.user import User


def _infer_tech_keywords(company: Company) -> set[str]:
    """Infer tech keywords from company name and metadata."""
    keywords: set[str] = set()
    name_lower = (company.name or "").lower()

    if any(kw in name_lower for kw in ["data", "analytics", "ml", "ai", "machine learning"]):
        keywords.update(["python", "sql", "machine learning", "data engineering", "pytorch", "scikit-learn", "pandas"])

    if any(kw in name_lower for kw in ["cloud", "infra", "platform", "devops", "sre"]):
        keywords.update(["aws", "gcp", "azure", "docker", "kubernetes", "terraform", "ci/cd"])

    if any(kw in name_lower for kw in ["web", "frontend", "fullstack"]):
        keywords.update(["javascript", "typescript", "react", "nextjs", "nodejs"])

    if any(kw in name_lower for kw in ["security", "cyber", "infosec"]):
        keywords.update(["security", "networking", "linux", "python"])

    # Always include ats_type if present
    if company.ats_type:
        keywords.add(company.ats_type.lower())

    return keywords


async def match_users_to_company(company_id: UUID, db: AsyncSession) -> list[dict]:
    """
    Compare the tech stack inferred from a company against each active user's skills.

    Returns a list of dicts with user_id, name, email, match_score, matching_skills
    ordered by match_score DESC. Only users with match_score > 0 are included.
    """
    company = await db.get(Company, company_id)
    if company is None:
        return []

    tech_keywords = _infer_tech_keywords(company)
    tier_multiplier = 1.2 if company.tier == "A" else 1.0

    # Load all users
    result = await db.scalars(select(User))
    users = list(result)

    matches: list[dict] = []
    for user in users:
        user_skills_raw = (user.strong_skills or []) + (user.technical_interests or [])
        user_skills_lower = {s.lower() for s in user_skills_raw}

        matching = tech_keywords & user_skills_lower
        if not matching:
            continue

        raw_score = len(matching) * 10
        match_score = int(raw_score * tier_multiplier)

        matches.append(
            {
                "user_id": str(user.id),
                "name": user.name,
                "email": user.email,
                "match_score": match_score,
                "matching_skills": sorted(matching),
            }
        )

    matches.sort(key=lambda x: x["match_score"], reverse=True)
    return matches
