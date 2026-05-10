from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.routers.applications import router as applications_router
from app.routers.companies import router as companies_router
from app.routers.contacts import router as contacts_router
from app.routers.dashboard import router as dashboard_router
from app.routers.discovery import discovery_router, job_postings_router
from app.routers.discovery_sources import router as discovery_sources_router
from app.routers.reminders import router as reminders_router
from app.routers.users import router as users_router

app = FastAPI(title=settings.app_name)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok", "service": "backend"}


app.include_router(applications_router)
app.include_router(companies_router)
app.include_router(contacts_router)
app.include_router(dashboard_router)
app.include_router(discovery_router)
app.include_router(discovery_sources_router)
app.include_router(job_postings_router)
app.include_router(reminders_router)
app.include_router(users_router)
