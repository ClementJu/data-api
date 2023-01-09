from datetime import datetime

from sqlalchemy import Boolean, Column, DateTime, Integer, String

from app.data.database import Base


class DialogDataEntityBase:
    id = Column(Integer, primary_key=True)
    customer_id = Column(String, index=True)
    dialog_id = Column(String)
    text = Column(String)
    language = Column(String)
    received_at_timestamp_utc = Column(DateTime, index=True, default=datetime.utcnow())


class DialogDataEntity(Base, DialogDataEntityBase):
    __tablename__ = 'dialog_data'


class TemporaryDialogDataEntity(Base, DialogDataEntityBase):
    __tablename__ = 'temporary_dialog_data'


class ConsentEntity(Base):
    __tablename__ = 'consents'
    id = Column(Integer, primary_key=True)
    dialog_id = Column(String)
    has_given_consent = Column(Boolean)
    received_at_timestamp_utc = Column(DateTime, index=True, default=datetime.utcnow())
