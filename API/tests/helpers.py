from pathlib import Path
from typing import Dict, List

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.data.database import Base, get_db
from app.data.entities import ConsentEntity, DialogDataEntity, TemporaryDialogDataEntity
from app.main import app


class HelperTestBase:
    def __init__(self) -> None:
        self.database_location = './test.db'
        self.DATABASE_URI = f'sqlite:///{self.database_location}'
        self.engine = create_engine(
            self.DATABASE_URI, connect_args={"check_same_thread": False}
        )
        Base.metadata.create_all(bind=self.engine)
        self.testing_session_local = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
        app.dependency_overrides[get_db] = self.override_get_db
        self.client = TestClient(app)

    def override_get_db(self) -> Session:
        try:
            db = self.testing_session_local()
            yield db
        finally:
            db.close()

    def get_test_client_with_database(self) -> TestClient:
        return self.client

    def remove_test_database(self) -> None:
        database_location_path = Path(self.database_location)
        database_location_path.unlink(missing_ok=True)

    def empty_database(self) -> None:
        db = self.testing_session_local()
        db.query(DialogDataEntity).delete()
        db.query(TemporaryDialogDataEntity).delete()
        db.query(ConsentEntity).delete()
        db.commit()

    def get_database(self) -> Session:
        return self.testing_session_local()

    def get_test_payloads_save_dialog_data(self) -> List[Dict[str, str]]:
        return [
            {
                'text': 'Good afternoon chatbot',
                'language': 'EN'
            },
            {
                'text': 'Hello!',
                'language': 'EN'
            },
            {
                'text': 'What\'s up?',
                'language': 'EN'
            }
        ]


test_base = HelperTestBase()
test_client = test_base.client
