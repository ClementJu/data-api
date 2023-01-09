from datetime import datetime
from typing import List, Optional

from sqlalchemy.orm import Session

from app.data.entities import DialogDataEntity, TemporaryDialogDataEntity
from app.data.models import DialogDataCreateModel, DialogDataModel


def save_dialog_data(dialog_data: DialogDataCreateModel, customer_id: str,
                     dialog_id: str, db: Session) -> DialogDataModel:
    dialog_data_to_insert = TemporaryDialogDataEntity(
        customer_id=customer_id,
        dialog_id=dialog_id,
        language=dialog_data.language.lower(),
        text=dialog_data.text,
        received_at_timestamp_utc=datetime.utcnow()
    )
    db.add(dialog_data_to_insert)
    db.commit()
    db.refresh(dialog_data_to_insert)
    return dialog_data_to_insert


def get_dialog_data(language: Optional[str], customer_id: Optional[str], db: Session) -> List[DialogDataModel]:
    query_builder = db.query(DialogDataEntity)

    if language is not None and language != '':
        query_builder = query_builder.filter(DialogDataEntity.language == language.lower())

    if customer_id is not None and customer_id != '':
        query_builder = query_builder.filter(DialogDataEntity.customer_id == customer_id)

    matching_data = query_builder.order_by(DialogDataEntity.received_at_timestamp_utc.desc()).all()
    return matching_data
