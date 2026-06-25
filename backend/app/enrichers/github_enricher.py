import os

from app.enrichers.base import BaseEnricher


class GitHubEnricher(BaseEnricher):
    def is_configured(self) -> bool:
        return bool(os.getenv("GITHUB_TOKEN"))

    async def find_people(self, company, db):
        if not self.is_configured():
            print(f"[GitHubEnricher] GITHUB_TOKEN not set. Skipping enrichment for {company.name}")
            return []
        # TODO: implement real GitHub search when token is available
        # Would: search GitHub users with company in profile,
        # extract emails from public commits
        return []
