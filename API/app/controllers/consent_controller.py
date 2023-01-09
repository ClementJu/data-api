from fastapi import APIRouter, Body, Depends, Path
from sqlalchemy.orm import Session

import app.services.consent_service as service
from app.data.database import get_db
from app.data.models import ConsentModel
from app.helpers.logging_helper import LoggingRoute

consent_router = APIRouter(
    prefix='/consents',
    tags=['consents'],
    responses={404: {'description': 'Not found'}},
    route_class=LoggingRoute
)


@consent_router.post("/{dialogId}", response_model=ConsentModel)
def save_user_consent(dialog_id: str = Path(None, alias="dialogId"),
                      has_given_consent: bool = Body(default=None, embed=False),
                      db: Session = Depends(get_db)) -> ConsentModel:
    return service.save_user_consent(dialog_id=dialog_id, has_given_consent=has_given_consent, db=db)
