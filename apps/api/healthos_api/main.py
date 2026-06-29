from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware

from healthos_api.config import get_settings
from healthos_api.models import User
from healthos_api.routes import activities, admin, auth, experiments, garmin, health, imports, insights, manual_events, metrics, recommendations
from healthos_api.schemas import MeResponse
from healthos_api.security import get_current_user

settings = get_settings()

app = FastAPI(title="Personal Health OS API", version="0.1.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(garmin.router)
app.include_router(health.router)
app.include_router(metrics.router)
app.include_router(activities.router)
app.include_router(insights.router)
app.include_router(imports.router)
app.include_router(recommendations.router)
app.include_router(manual_events.router)
app.include_router(experiments.router)
app.include_router(admin.router)


@app.get("/me", response_model=MeResponse)
def me(user: User = Depends(get_current_user)) -> MeResponse:
    return MeResponse(id=user.id, email=user.email, is_admin=user.is_admin)


@app.get("/healthz")
def healthz() -> dict:
    return {"status": "ok"}
