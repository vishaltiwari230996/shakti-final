from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api import routes, accounts, catalogue
from app.database import init_db
import os

app = FastAPI(title="Shakti 1.2 Enterprise API")


@app.on_event("startup")
def _startup_init_db() -> None:
    # Create tables, seed default plans, and install admin view (Postgres only).
    # Disable via INIT_DB_ON_STARTUP=false in production once Alembic is set up.
    if os.getenv("INIT_DB_ON_STARTUP", "true").lower() == "true":
        init_db()

def get_allowed_origins():
    configured_origins = os.getenv("ALLOWED_ORIGINS", "").strip()
    environment = os.getenv("APP_ENV", "development").lower()

    if configured_origins:
        return [origin.strip() for origin in configured_origins.split(",") if origin.strip()]

    if environment in {"development", "dev", "local"}:
        return [
            "http://localhost:5173",
            "http://127.0.0.1:5173",
        ]

    raise RuntimeError("ALLOWED_ORIGINS must be configured outside development.")


allowed_origins = get_allowed_origins()

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(routes.router, prefix="/api")
app.include_router(accounts.router, prefix="/api")
app.include_router(catalogue.router, prefix="/api")

@app.get("/")
def read_root():
    return {"message": "Shakti 1.2 Enterprise API is running"}
