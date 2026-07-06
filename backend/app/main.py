from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.auth import verify_api_key
from app.config import settings
from app.routers.applications import router as applications_router
from app.routers.companies import router as companies_router
from app.routers.contacts import router as contacts_router
from app.routers.dashboard import router as dashboard_router
from app.routers.discovery import discovery_router, job_postings_router
from app.routers.discovery_sources import router as discovery_sources_router
from app.routers.interviews import router as interviews_router
from app.routers.outreach import router as outreach_router
from app.routers.reminders import router as reminders_router
from app.routers.tech_matcher import router as tech_matcher_router
from app.routers.templates import router as templates_router
from app.routers.users import router as users_router
from app.routers.visa import router as visa_router

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


# Every real router requires the API key (header X-API-Key) — /health above
# is the only public route, since container/uptime health checks need it.
# Looping over a list (instead of one dependencies=[...] per include_router
# call) means a router added here later can't accidentally ship unprotected.
_ROUTERS = (
    applications_router,
    companies_router,
    contacts_router,
    dashboard_router,
    discovery_router,
    discovery_sources_router,
    interviews_router,
    job_postings_router,
    outreach_router,
    reminders_router,
    tech_matcher_router,
    templates_router,
    users_router,
    visa_router,
)
for _router in _ROUTERS:
    app.include_router(_router, dependencies=[Depends(verify_api_key)])
