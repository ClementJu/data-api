from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import inspect

import app.helpers.logging_helper as logging_helper
from app.config.config import settings
from app.controllers.consent_controller import consent_router
from app.controllers.data_controller import data_router
from app.controllers.health_controller import health_router
from app.data.database import Base, engine

app = FastAPI(title=settings.PROJECT_NAME)

app.include_router(health_router)
app.include_router(data_router)
app.include_router(consent_router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[str(origin) for origin in settings.BACKEND_CORS_ORIGINS],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

logging_helper.set_up_logging()

if not inspect(engine).has_table("temporary_dialog_data"):
    Base.metadata.create_all(engine)
