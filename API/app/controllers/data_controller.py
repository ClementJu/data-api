from typing import List, Optional

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

import app.services.data_service as service
from app.data.database import get_db
from app.data.models import DialogDataCreateModel, DialogDataModel
from app.helpers.logging_helper import LoggingRoute

data_router = APIRouter(
    prefix='/data',
    tags=['data'],
    responses={404: {'description': 'Not found'}},
    route_class=LoggingRoute
)


@data_router.post("/{customer_id}/{dialog_id}", response_model=DialogDataModel)
def save_dialog_data(dialog_data: DialogDataCreateModel, customer_id: str,
                     dialog_id: str, db: Session = Depends(get_db)) -> DialogDataModel:
    return service.save_dialog_data(dialog_data=dialog_data, customer_id=customer_id, dialog_id=dialog_id, db=db)


@data_router.get("", response_model=List[DialogDataModel])
def get_dialog_data(language: Optional[str] = None, customer_id: Optional[str] = None,
                    db: Session = Depends(get_db)) -> List[DialogDataModel]:
    return service.get_dialog_data(language=language, customer_id=customer_id, db=db)
