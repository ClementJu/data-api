from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.data.entities import ConsentEntity, DialogDataEntity, TemporaryDialogDataEntity
from app.data.models import ConsentCreateModel, ConsentModel


def save_user_consent(consent: ConsentCreateModel, dialog_id: str, db: Session) -> ConsentModel:
    existing_consent = db.query(ConsentEntity).filter(ConsentEntity.dialog_id == dialog_id).first()

    if existing_consent is not None:
        raise HTTPException(status_code=409, detail=f'Consent was already given or denied for dialog_id {dialog_id}')

    existing_temporary_data = (db.query(TemporaryDialogDataEntity)
                               .filter(TemporaryDialogDataEntity.dialog_id == dialog_id).all())

    if len(existing_temporary_data) == 0:
        raise HTTPException(status_code=404, detail=f'Cannot give consent: no temporary data for dialog_id {dialog_id}')

    consent_to_insert = ConsentEntity(
        has_given_consent=consent.has_given_consent,
        dialog_id=dialog_id
    )

    db.add(consent_to_insert)

    for temporary_entry in existing_temporary_data:
        if consent.has_given_consent:
            db.add(DialogDataEntity(
                customer_id=temporary_entry.customer_id,
                text=temporary_entry.text,
                language=temporary_entry.language,
                received_at_timestamp_utc=temporary_entry.received_at_timestamp_utc,
                dialog_id=temporary_entry.dialog_id
            ))

        db.delete(temporary_entry)

    db.commit()
    db.refresh(consent_to_insert)
    return consent_to_insert
