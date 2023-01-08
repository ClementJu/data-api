from datetime import datetime

from sqlalchemy.orm import Session

from app.data.entities import TemporaryDialogDataEntity
from app.data.models import DialogDataCreateModel, DialogDataModel


def save_dialog_data(dialog_data: DialogDataCreateModel, customer_id: str,
                     dialog_id: str, db: Session) -> DialogDataModel:
    dialog_data_to_insert = TemporaryDialogDataEntity(
        customer_id=customer_id,
        dialog_id=dialog_id,
        language=dialog_data.language,
        text=dialog_data.text,
        received_at_timestamp_utc=datetime.utcnow()
    )
    db.add(dialog_data_to_insert)
    db.commit()
    db.refresh(dialog_data_to_insert)
    return dialog_data_to_insert
