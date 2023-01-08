from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

import app.helpers.logging_helper as logging_helper
from app.controllers.health_controller import health_router
from app.core.config import settings

app = FastAPI(title=settings.PROJECT_NAME)

app.include_router(health_router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[str(origin) for origin in settings.BACKEND_CORS_ORIGINS],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

logging_helper.set_up_logging()
