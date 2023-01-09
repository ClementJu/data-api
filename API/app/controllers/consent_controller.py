from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

import app.services.consent_service as service
from app.data.database import get_db
from app.data.models import ConsentCreateModel, ConsentModel
from app.helpers.logging_helper import LoggingRoute

consent_router = APIRouter(
    prefix='/consents',
    tags=['consents'],
    responses={404: {'description': 'Not found'}},
    route_class=LoggingRoute
)


@consent_router.post("/{dialog_id}", response_model=ConsentModel)
def save_user_consent(consent: ConsentCreateModel, dialog_id: str, db: Session = Depends(get_db)) -> ConsentModel:
    return service.save_user_consent(consent=consent, dialog_id=dialog_id, db=db)
