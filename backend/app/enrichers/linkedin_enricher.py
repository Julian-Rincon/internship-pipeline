import os

from app.enrichers.base import BaseEnricher


class LinkedInEnricher(BaseEnricher):
    def is_configured(self) -> bool:
        return bool(os.getenv("APIFY_API_TOKEN"))

    async def find_people(self, company, db):
        if not self.is_configured():
            print(f"[LinkedInEnricher] APIFY_API_TOKEN not set. Skipping enrichment for {company.name}")
            return []
        # TODO: implement real LinkedIn scraping via Apify when token is available
        # Would: call Apify LinkedIn People Search actor with company name
        return []
