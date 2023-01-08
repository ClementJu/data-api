from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

import app.helpers.logging_helper as logging_helper
from app.config.config import settings
from app.controllers.data_controller import data_router
from app.controllers.health_controller import health_router

app = FastAPI(title=settings.PROJECT_NAME)

app.include_router(health_router)
app.include_router(data_router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[str(origin) for origin in settings.BACKEND_CORS_ORIGINS],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

logging_helper.set_up_logging()
