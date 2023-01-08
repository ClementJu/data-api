from pathlib import Path

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.data.database import Base, get_db
from app.main import app


class HelperTestBase:
    def __init__(self) -> None:
        self.database_location = './test.db'
        self.DATABASE_URI = f'sqlite:///{self.database_location}'
        self.engine = create_engine(
            self.DATABASE_URI, connect_args={"check_same_thread": False}
        )
        Base.metadata.create_all(bind=self.engine)
        self.testingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
        app.dependency_overrides[get_db] = self.override_get_db
        self.client = TestClient(app)

    def override_get_db(self) -> Session:
        try:
            db = self.testingSessionLocal()
            yield db
        finally:
            db.close()

    def get_test_client_with_database(self) -> TestClient:
        return self.client

    def remove_test_database(self) -> None:
        database_location_path = Path(self.database_location)
        database_location_path.unlink(missing_ok=True)


test_base = HelperTestBase()
test_client = test_base.client
