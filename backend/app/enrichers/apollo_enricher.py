import os

from app.enrichers.base import BaseEnricher


class ApolloEnricher(BaseEnricher):
    def is_configured(self) -> bool:
        return bool(os.getenv("APOLLO_API_KEY"))

    async def find_people(self, company, db):
        if not self.is_configured():
            print(f"[ApolloEnricher] APOLLO_API_KEY not set. Skipping enrichment for {company.name}")
            return []
        # TODO: implement real Apollo.io people search when API key is available
        # Would: POST /v1/mixed_people/search with organization_domains
        return []
