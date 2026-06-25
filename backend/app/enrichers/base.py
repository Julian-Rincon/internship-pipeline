from abc import ABC, abstractmethod

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.company import Company


class BaseEnricher(ABC):
    @abstractmethod
    def is_configured(self) -> bool:
        """Check if required API keys are set."""
        ...

    @abstractmethod
    async def find_people(self, company: Company, db: AsyncSession) -> list[dict]:
        """
        Returns a list of potential contacts for the company.

        Each item should be a dict with keys:
            full_name, role, email, source, affinity_type, affinity_score
        """
        ...
