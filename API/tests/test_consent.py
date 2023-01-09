from typing import Dict

from starlette.responses import Response
from tests.helpers import test_base, test_client

from app.data.entities import ConsentEntity, DialogDataEntity, TemporaryDialogDataEntity


def test_save_consent_should_work() -> None:
    test_base.empty_database()

    # Case True
    _insert_dialog_data(dialog_id='did34')

    test_client.post(
        '/consents/did34',
        json={
            'has_given_consent': 'true'
        }
    )
    db = test_base.get_database()
    consents = db.query(ConsentEntity).all()
    assert len(consents) == 1
    assert consents[0].has_given_consent
    assert consents[0].dialog_id == 'did34'

    consents_for_given_dialog_id = db.query(ConsentEntity).filter(ConsentEntity.dialog_id == 'did34').all()
    assert len(consents_for_given_dialog_id) == 1
    assert consents_for_given_dialog_id[0].has_given_consent
    assert consents_for_given_dialog_id[0].dialog_id == 'did34'

    # Case False
    _insert_dialog_data(dialog_id='did55')

    test_client.post(
        '/consents/did55',
        json={
            'has_given_consent': 'false'
        }
    )

    consents_after_two_insertions = db.query(ConsentEntity).all()
    assert len(consents_after_two_insertions) == 2

    consents_for_given_dialog_id = db.query(ConsentEntity).filter(ConsentEntity.dialog_id == 'did55').all()
    assert len(consents_for_given_dialog_id) == 1
    assert not consents_for_given_dialog_id[0].has_given_consent
    assert consents_for_given_dialog_id[0].dialog_id == 'did55'


def test_save_consent_should_throw_if_no_temporary_data_for_dialog_id() -> None:
    test_base.empty_database()
    response = test_client.post(
        '/consents/did55',
        json={
            'has_given_consent': 'true'
        }
    )
    assert response.status_code == 404


def test_save_consent_should_throw_if_consent_was_already_given() -> None:
    test_base.empty_database()

    _insert_dialog_data(dialog_id='did55')

    response = test_client.post(
        '/consents/did55',
        json={
            'has_given_consent': 'true'
        }
    )
    assert response.status_code == 200

    response = test_client.post(
        '/consents/did55',
        json={
            'has_given_consent': 'true'
        }
    )
    assert response.status_code == 409

    response = test_client.post(
        '/consents/did55',
        json={
            'has_given_consent': 'false'
        }
    )
    assert response.status_code == 409


def test_save_consent_should_move_data_if_consent_is_given() -> None:
    test_base.empty_database()
    db = test_base.get_database()

    _insert_dialog_data(dialog_id='did55')

    assert len(db.query(ConsentEntity).all()) == 0
    assert len(db.query(TemporaryDialogDataEntity).all()) == 1
    assert len(db.query(DialogDataEntity).all()) == 0

    response = test_client.post(
        '/consents/did55',
        json={
            'has_given_consent': 'true'
        }
    )
    assert response.status_code == 200

    assert len(db.query(ConsentEntity).all()) == 1
    assert len(db.query(TemporaryDialogDataEntity).all()) == 0
    assert len(db.query(DialogDataEntity).all()) == 1


def test_save_consent_should_erase_data_if_consent_is_not_given() -> None:
    test_base.empty_database()

    _insert_dialog_data(dialog_id='did55')

    db = test_base.get_database()

    assert len(db.query(ConsentEntity).all()) == 0
    assert len(db.query(TemporaryDialogDataEntity).all()) == 1
    assert len(db.query(DialogDataEntity).all()) == 0

    response = test_client.post(
        '/consents/did55',
        json={
            'has_given_consent': 'false'
        }
    )
    assert response.status_code == 200

    assert len(db.query(ConsentEntity).all()) == 1
    assert len(db.query(TemporaryDialogDataEntity).all()) == 0
    assert len(db.query(DialogDataEntity).all()) == 0


def _get_first_dialog_data_payload() -> Dict[str, str]:
    dialog_data_payloads = test_base.get_test_payloads_save_dialog_data()
    return dialog_data_payloads[0]


def _insert_dialog_data(payload: Dict[str, str] = None, customer_id: str = 'id12',
                        dialog_id: str = 'did55') -> Response:
    return test_client.post(
        f'/data/{customer_id}/{dialog_id}',
        json=_get_first_dialog_data_payload() if payload is None else payload
    )
