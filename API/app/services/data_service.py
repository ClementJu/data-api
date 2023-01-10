from datetime import datetime, timedelta
from typing import List, Optional

from sqlalchemy.orm import Session

from app.config.config import settings
from app.data.entities import ConsentEntity, DialogDataEntity, TemporaryDialogDataEntity
from app.data.models import AnomalyDataModel, DialogDataCreateModel, DialogDataModel


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


def get_dialog_data(language: Optional[str], customer_id: Optional[str], db: Session,
                    skip: Optional[int] = None, limit: Optional[int] = None) -> List[DialogDataModel]:
    query_builder = db.query(DialogDataEntity)

    if language is not None and language != '':
        query_builder = query_builder.filter(DialogDataEntity.language == language.lower())

    if customer_id is not None and customer_id != '':
        query_builder = query_builder.filter(DialogDataEntity.customer_id == customer_id)

    # Order by has to be applied before skip and limit
    query_builder = query_builder.order_by(DialogDataEntity.received_at_timestamp_utc.desc())

    if skip is not None and skip > 0:
        query_builder = query_builder.offset(skip)

    if limit is not None and limit > 0:
        query_builder = query_builder.limit(limit)

    matching_data = query_builder.all()
    return matching_data


def get_anomalies(db: Session) -> List[AnomalyDataModel]:
    limit_date_anomaly = datetime.utcnow() - timedelta(milliseconds=settings.ANOMALY_PERIOD_MS)
    consents_given = db.query(ConsentEntity.dialog_id)

    """
    An anomaly is defined as an entry in the Temporary Data Table if no consent was given for the related dialog ID
    and if it was received before a specific limit date, computed as follows: "NOW - ANOMALY_PERIOD"
    """
    anomalies = (db.query(TemporaryDialogDataEntity)
                 .filter(TemporaryDialogDataEntity.received_at_timestamp_utc < limit_date_anomaly)
                 .filter(~TemporaryDialogDataEntity.dialog_id.in_(consents_given)))

    return list(map(lambda temporary_data_row: AnomalyDataModel(
        dialog_id=temporary_data_row.dialog_id,
        customer_id=temporary_data_row.customer_id,
        received_at_timestamp_utc=temporary_data_row.received_at_timestamp_utc
    ), anomalies))
