from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.core.database import init_db
from app.api.routes import health
from app.api.v1 import (
    analytics,
    audits,
    contracts,
    copilot,
    diversity,
    integration,
    onboarding,
    performance,
    po_line_items,
    purchase_orders,
    risk,
    settings as settings_routes,
    surveys,
    sustainability,
    vendors,
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    yield


app = FastAPI(
    title=settings.app_name,
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health.router, prefix="/health", tags=["health"])
app.include_router(vendors.router, prefix="/api/v1/vendors", tags=["vendors"])
app.include_router(
    purchase_orders.router, prefix="/api/v1/purchase-orders", tags=["purchase-orders"]
)
app.include_router(
    po_line_items.router, prefix="/api/v1/po-line-items", tags=["po-line-items"]
)
app.include_router(settings_routes.router, prefix="/api/v1/settings", tags=["settings"])
app.include_router(copilot.router, prefix="/api/v1/copilot", tags=["copilot"])
app.include_router(onboarding.router, prefix="/api/v1/onboarding", tags=["onboarding"])
app.include_router(performance.router, prefix="/api/v1/performance", tags=["performance"])
app.include_router(risk.router, prefix="/api/v1/risk", tags=["risk"])
app.include_router(contracts.router, prefix="/api/v1/contracts", tags=["contracts"])
app.include_router(analytics.router, prefix="/api/v1/analytics", tags=["analytics"])
app.include_router(integration.router, prefix="/api/v1/integration", tags=["integration"])
app.include_router(sustainability.router, prefix="/api/v1/sustainability", tags=["sustainability"])
app.include_router(diversity.router, prefix="/api/v1/diversity", tags=["diversity"])
app.include_router(surveys.router, prefix="/api/v1/surveys", tags=["surveys"])
app.include_router(audits.router, prefix="/api/v1/audits", tags=["audits"])
