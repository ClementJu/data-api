from pathlib import Path
from typing import Dict, List

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from starlette.responses import Response

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
        self.test_client = TestClient(app)

    def override_get_db(self) -> Session:
        try:
            db = self.testing_session_local()
            yield db
        finally:
            db.close()

    def get_test_client(self) -> TestClient:
        return self.test_client

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

    def insert_dialog_data(self, payload: Dict[str, str] = None, customer_id: str = 'id12',
                           dialog_id: str = 'did55') -> Response:
        return self.test_client.post(
            f'/data/{customer_id}/{dialog_id}',
            json=HelperTestBase.get_first_dialog_data_payload() if payload is None else payload
        )

    @staticmethod
    def get_first_dialog_data_payload() -> Dict[str, str]:
        dialog_data_payloads = test_base.get_test_payloads_save_dialog_data()
        return dialog_data_payloads[0]

    def give_consent(self, has_given_consent: bool = True, dialog_id: str = 'did55') -> Response:
        return self.test_client.post(
            f'/consents/{dialog_id}',
            json={'has_given_consent': ('true' if has_given_consent else 'false')}
        )

    def get_dialog_data(self, query_string: str) -> Response:
        return self.test_client.get(
            f'/data{query_string}'
        )


test_base = HelperTestBase()
