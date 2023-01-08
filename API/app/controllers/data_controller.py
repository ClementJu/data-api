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
async def save_dialog_data(dialog_data: DialogDataCreateModel, customer_id: str,
                           dialog_id: str, db: Session = Depends(get_db)) -> DialogDataModel:
    return await service.save_dialog_data(dialog_data=dialog_data, customer_id=customer_id, dialog_id=dialog_id, db=db)
