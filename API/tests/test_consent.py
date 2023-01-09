from tests.helpers import test_base, test_client

from app.data.entities import ConsentEntity, DialogDataEntity, TemporaryDialogDataEntity


def test_save_consent_should_work() -> None:
    test_base.empty_database()
    dialog_data_payloads = test_base.get_test_payloads_save_dialog_data()

    # Case True
    test_client.post(
        '/data/id12/did34',
        json=dialog_data_payloads[0]
    )

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

    consents_dialog_id = db.query(ConsentEntity).filter(ConsentEntity.dialog_id == 'did34').all()
    assert len(consents_dialog_id) == 1
    assert consents_dialog_id[0].has_given_consent
    assert consents_dialog_id[0].dialog_id == 'did34'

    test_client.post(
        '/data/id12/did55',
        json=dialog_data_payloads[0]
    )

    test_client.post(
        '/consents/did55',
        json={
            'has_given_consent': 'false'
        }
    )

    # Case False
    consents2 = db.query(ConsentEntity).all()
    assert len(consents2) == 2

    consents_dialog_id = db.query(ConsentEntity).filter(ConsentEntity.dialog_id == 'did55').all()
    assert len(consents_dialog_id) == 1
    assert not consents_dialog_id[0].has_given_consent
    assert consents_dialog_id[0].dialog_id == 'did55'


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
    dialog_data_payloads = test_base.get_test_payloads_save_dialog_data()

    test_client.post(
        '/data/id12/did55',
        json=dialog_data_payloads[0]
    )

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
    dialog_data_payloads = test_base.get_test_payloads_save_dialog_data()

    test_client.post(
        '/data/id12/did55',
        json=dialog_data_payloads[0]
    )

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
    db = test_base.get_database()
    dialog_data_payloads = test_base.get_test_payloads_save_dialog_data()

    test_client.post(
        '/data/id12/did55',
        json=dialog_data_payloads[0]
    )

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
