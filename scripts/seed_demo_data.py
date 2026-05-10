import asyncio
from datetime import date

from sqlalchemy import select

from app.db import async_session_factory
from app.models.application import Application
from app.models.company import Company
from app.models.contact import Contact
from app.models.user import User


DEMO_COMPANIES = [
    {
        "name": "Northstar Robotics Demo",
        "domain": "northstar-robotics.demo.example",
        "tier": "A",
        "country": "Exampleland",
        "region": "EU",
        "careers_url": "https://northstar-robotics.demo.example/careers",
        "ats_type": "custom",
        "visa_friendly_intern": "unknown",
        "status": "active",
    },
    {
        "name": "Blue Orbit Systems Demo",
        "domain": "blue-orbit-systems.demo.example",
        "tier": "B",
        "country": "Sample Republic",
        "region": "USA",
        "careers_url": "https://blue-orbit-systems.demo.example/jobs",
        "ats_type": "custom",
        "visa_friendly_intern": "yellow",
        "status": "active",
    },
    {
        "name": "Cedar Cloud Labs Demo",
        "domain": "cedar-cloud-labs.demo.example",
        "tier": "C",
        "country": "Demo Federation",
        "region": "LATAM",
        "careers_url": "https://cedar-cloud-labs.demo.example/careers",
        "ats_type": "custom",
        "visa_friendly_intern": "unknown",
        "status": "active",
    },
]

DEMO_USERS = [
    {
        "name": "Alex Demo",
        "email": "alex.demo@demo.example",
        "role": "member",
        "profile_status": "ready",
        "github_handle": "alex-demo",
        "target_roles": ["backend intern", "platform intern"],
        "target_regions": ["EU", "USA"],
        "technical_interests": ["distributed systems", "databases"],
        "strong_skills": ["python", "sql"],
        "learning_goals": ["production APIs", "cloud infrastructure"],
        "internship_goals": "Find a backend internship with strong mentorship.",
    },
    {
        "name": "Sam Demo",
        "email": "sam.demo@demo.example",
        "role": "member",
        "profile_status": "in_progress",
        "target_roles": ["frontend intern", "full-stack intern"],
        "target_regions": ["USA", "LATAM"],
        "technical_interests": ["frontend systems", "developer tools"],
        "strong_skills": ["typescript", "react"],
        "learning_goals": ["product engineering", "testing"],
        "internship_goals": "Improve full-stack product delivery skills.",
    },
    {
        "name": "Taylor Demo",
        "email": "taylor.demo@demo.example",
        "role": "member",
        "profile_status": "incomplete",
        "target_roles": ["data intern", "ml platform intern"],
        "target_regions": ["EU"],
        "technical_interests": ["data pipelines", "ml systems"],
        "strong_skills": ["python"],
        "learning_goals": ["data modeling", "ml operations"],
        "internship_goals": "Explore data infrastructure internships.",
    },
]

DEMO_CONTACTS = [
    {
        "company_domain": "northstar-robotics.demo.example",
        "full_name": "Jordan Fictional",
        "role": "University Recruiting Lead",
        "email": "jordan.fictional@northstar-robotics.demo.example",
        "source": "manual",
        "affinity_type": "recruiter",
        "contacted": False,
    },
    {
        "company_domain": "blue-orbit-systems.demo.example",
        "full_name": "Casey Fictional",
        "role": "Backend Engineering Manager",
        "email": "casey.fictional@blue-orbit-systems.demo.example",
        "source": "manual",
        "affinity_type": "engineer",
        "contacted": True,
    },
    {
        "company_domain": "cedar-cloud-labs.demo.example",
        "full_name": "Morgan Fictional",
        "role": "Early Careers Coordinator",
        "email": "morgan.fictional@cedar-cloud-labs.demo.example",
        "source": "manual",
        "affinity_type": "unknown",
        "contacted": False,
    },
]

DEMO_APPLICATIONS = [
    {
        "company_domain": "northstar-robotics.demo.example",
        "user_email": "alex.demo@demo.example",
        "contact_email": "jordan.fictional@northstar-robotics.demo.example",
        "type": "formal",
        "status": "researching",
        "next_action": "Review internship requirements and prepare application notes.",
        "next_action_due": date(2027, 1, 15),
        "notes": "Demo record only. No real outreach planned.",
    },
    {
        "company_domain": "blue-orbit-systems.demo.example",
        "user_email": "sam.demo@demo.example",
        "contact_email": "casey.fictional@blue-orbit-systems.demo.example",
        "type": "networking",
        "status": "contacted",
        "next_action": "Track manual follow-up decision during weekly review.",
        "next_action_due": date(2027, 1, 22),
        "notes": "Demo contact marked as contacted for board visualization.",
    },
    {
        "company_domain": "cedar-cloud-labs.demo.example",
        "user_email": "taylor.demo@demo.example",
        "contact_email": "morgan.fictional@cedar-cloud-labs.demo.example",
        "type": "speculative",
        "status": "paused",
        "next_action": "Wait until profile reaches ready status.",
        "next_action_due": date(2027, 2, 5),
        "notes": "Demo record showing paused pipeline state.",
    },
]


async def get_one(session, model, **filters):
    result = await session.scalars(select(model).filter_by(**filters))
    return result.first()


async def main() -> None:
    async with async_session_factory() as session:
        companies_by_domain = {}
        for company_data in DEMO_COMPANIES:
            company = await get_one(session, Company, domain=company_data["domain"])
            if company is None:
                company = Company(**company_data)
                session.add(company)
                await session.flush()
            companies_by_domain[company.domain] = company

        users_by_email = {}
        for user_data in DEMO_USERS:
            user = await get_one(session, User, email=user_data["email"])
            if user is None:
                user = User(**user_data)
                session.add(user)
                await session.flush()
            users_by_email[user.email] = user

        contacts_by_email = {}
        for contact_data in DEMO_CONTACTS:
            contact_email = contact_data["email"]
            contact = await get_one(session, Contact, email=contact_email)
            if contact is None:
                company = companies_by_domain[contact_data["company_domain"]]
                contact = Contact(
                    company_id=company.id,
                    full_name=contact_data["full_name"],
                    role=contact_data["role"],
                    email=contact_email,
                    source=contact_data["source"],
                    affinity_type=contact_data["affinity_type"],
                    contacted=contact_data["contacted"],
                )
                session.add(contact)
                await session.flush()
            contacts_by_email[contact.email] = contact

        for application_data in DEMO_APPLICATIONS:
            company = companies_by_domain[application_data["company_domain"]]
            user = users_by_email[application_data["user_email"]]
            contact = contacts_by_email[application_data["contact_email"]]
            existing = await get_one(
                session,
                Application,
                company_id=company.id,
                user_id=user.id,
                contact_id=contact.id,
                type=application_data["type"],
            )
            if existing is None:
                session.add(
                    Application(
                        company_id=company.id,
                        user_id=user.id,
                        contact_id=contact.id,
                        type=application_data["type"],
                        status=application_data["status"],
                        next_action=application_data["next_action"],
                        next_action_due=application_data["next_action_due"],
                        notes=application_data["notes"],
                    )
                )

        await session.commit()

    print("Demo data loaded. All records are fictional and use demo.example domains.")


if __name__ == "__main__":
    asyncio.run(main())
