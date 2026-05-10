from pydantic import BaseModel


class DashboardSummary(BaseModel):
    total_companies: int
    total_users: int
    total_contacts: int
    total_applications: int
    applications_by_status: dict[str, int]

