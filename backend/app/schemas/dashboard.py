from pydantic import BaseModel


class DashboardSummary(BaseModel):
    total_companies: int
    total_users: int
    total_contacts: int
    total_applications: int
    unclaimed_companies: int
    claimed_companies: int
    paused_companies: int
    done_companies: int
    applications_by_status: dict[str, int]
