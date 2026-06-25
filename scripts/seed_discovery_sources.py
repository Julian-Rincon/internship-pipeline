"""
Seed real discovery sources for internship pipeline.

Adds:
- GetOnBoard: global search (Latam/Spain focused, data/AI/dev roles)
- Greenhouse boards: companies known for internship programs
- Lever boards: companies with early-career roles
- Ashby boards: startups with internship programs

Run after migrations:
    docker compose exec backend sh -c "PYTHONPATH=/app python scripts/seed_discovery_sources.py"
"""

import asyncio
import sys

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from app.config import settings
from app.models.discovery_source import DiscoverySource


SOURCES = [
    # ── GetOnBoard (Latam/Spain — no source_key needed, uses internal keywords) ──
    {
        "name": "GetOnBoard — Global Search",
        "source_type": "getonboard",
        "source_key": "global",
        "company_hint": None,
        "country": None,
        "region": "Latam / Remote",
        "enabled": True,
    },

    # ── Greenhouse — internship programs by board token ────────────────────────
    {
        "name": "Shopify Internships",
        "source_type": "greenhouse",
        "source_key": "shopify",
        "company_hint": "Shopify",
        "country": "Canada",
        "region": "Remote",
        "enabled": False,
    },
    {
        "name": "Twilio Internships",
        "source_type": "greenhouse",
        "source_key": "twilio",
        "company_hint": "Twilio",
        "country": "USA",
        "region": "Remote",
        "enabled": True,
    },
    {
        "name": "HashiCorp Internships",
        "source_type": "greenhouse",
        "source_key": "hashicorp",
        "company_hint": "HashiCorp",
        "country": "USA",
        "region": "Remote",
        "enabled": False,
    },
    {
        "name": "Databricks Internships",
        "source_type": "greenhouse",
        "source_key": "databricks",
        "company_hint": "Databricks",
        "country": "USA",
        "region": "Remote",
        "enabled": True,
    },
    {
        "name": "Figma Internships",
        "source_type": "greenhouse",
        "source_key": "figma",
        "company_hint": "Figma",
        "country": "USA",
        "region": "Remote",
        "enabled": True,
    },
    {
        "name": "Cloudflare Internships",
        "source_type": "greenhouse",
        "source_key": "cloudflare",
        "company_hint": "Cloudflare",
        "country": "USA",
        "region": "Remote",
        "enabled": True,
    },
    {
        "name": "Vercel Internships",
        "source_type": "greenhouse",
        "source_key": "vercel",
        "company_hint": "Vercel",
        "country": "USA",
        "region": "Remote",
        "enabled": True,
    },

    # ── Greenhouse (continued) — verified board tokens ────────────────────────
    {
        "name": "Stripe Internships",
        "source_type": "greenhouse",
        "source_key": "stripe",
        "company_hint": "Stripe",
        "country": "USA",
        "region": "Remote",
        "enabled": True,
    },
    {
        "name": "Airtable Internships",
        "source_type": "greenhouse",
        "source_key": "airtable",
        "company_hint": "Airtable",
        "country": "USA",
        "region": "Remote",
        "enabled": True,
    },
    {
        "name": "Scale AI Internships",
        "source_type": "greenhouse",
        "source_key": "scaleai",
        "company_hint": "Scale AI",
        "country": "USA",
        "region": "Remote",
        "enabled": True,
    },
    {
        "name": "Anthropic Internships",
        "source_type": "greenhouse",
        "source_key": "anthropic",
        "company_hint": "Anthropic",
        "country": "USA",
        "region": "Remote",
        "enabled": True,
    },

    # ── Ashby — verified board names ───────────────────────────────────────────
    {
        "name": "Replit Internships",
        "source_type": "ashby",
        "source_key": "replit",
        "company_hint": "Replit",
        "country": "USA",
        "region": "Remote",
        "enabled": True,
    },
    {
        "name": "Perplexity AI Internships",
        "source_type": "ashby",
        "source_key": "perplexity",
        "company_hint": "Perplexity AI",
        "country": "USA",
        "region": "Remote",
        "enabled": True,
    },
    {
        "name": "Cohere Internships",
        "source_type": "ashby",
        "source_key": "cohere",
        "company_hint": "Cohere",
        "country": "Canada",
        "region": "Remote",
        "enabled": True,
    },
    {
        "name": "Linear Internships",
        "source_type": "ashby",
        "source_key": "linear",
        "company_hint": "Linear",
        "country": "USA",
        "region": "Remote",
        "enabled": True,
    },
    {
        "name": "Notion Internships",
        "source_type": "ashby",
        "source_key": "notion",
        "company_hint": "Notion",
        "country": "USA",
        "region": "Remote",
        "enabled": True,
    },
]


async def seed(session: AsyncSession) -> None:
    added = 0
    skipped = 0
    for src_data in SOURCES:
        existing = await session.scalar(
            select(DiscoverySource).where(
                DiscoverySource.source_type == src_data["source_type"],
                DiscoverySource.source_key == src_data["source_key"],
            )
        )
        if existing is not None:
            print(f"  SKIP (exists): {src_data['name']}")
            skipped += 1
            continue

        session.add(DiscoverySource(**src_data))
        print(f"  ADD: {src_data['name']}")
        added += 1

    await session.commit()
    print(f"\n✅ Done — {added} added, {skipped} skipped.")


async def main() -> None:
    engine = create_async_engine(settings.database_url, echo=False)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with async_session() as session:
        await seed(session)

    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(main())
