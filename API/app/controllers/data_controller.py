from typing import List, Optional

from fastapi import APIRouter, Depends, Path, Query
from sqlalchemy.orm import Session

import app.services.data_service as service
from app.data.database import get_db
from app.data.models import AnomalyDataModel, DialogDataCreateModel, DialogDataModel
from app.helpers.logging_helper import LoggingRoute

data_router = APIRouter(
    prefix='/data',
    tags=['data'],
    responses={404: {'description': 'Not found'}},
    route_class=LoggingRoute
)


@data_router.post("/{customerId}/{dialogId}", response_model=DialogDataModel)
def save_dialog_data(dialog_data: DialogDataCreateModel, customer_id: str = Path(None, alias="customerId"),
                     dialog_id: str = Path(None, alias="dialogId"), db: Session = Depends(get_db)) -> DialogDataModel:
    return service.save_dialog_data(dialog_data=dialog_data, customer_id=customer_id, dialog_id=dialog_id, db=db)


@data_router.get("/", response_model=List[DialogDataModel])
def get_dialog_data(language: Optional[str] = Query(None, alias='language'),
                    customer_id: Optional[str] = Query(None, alias='customerId'),
                    db: Session = Depends(get_db)) -> List[DialogDataModel]:
    return service.get_dialog_data(language=language, customer_id=customer_id, db=db)


@data_router.get("/anomaly", response_model=List[AnomalyDataModel])
def get_anomalies(db: Session = Depends(get_db)) -> List[AnomalyDataModel]:
    """
    Additional endpoint that checks whether conversational data has been stored for a long time without receiving
    related consent information. No consent information does not mean that the user allows us to use his data,
    nor does it mean that he refuses consent.
    This endpoint could be used by any data administrator to be informed about the presence of old data. This person
    could then decide to permanently delete this data manually.
    """
    return service.get_anomalies(db=db)
