from tests.helpers import test_base

from app.data.entities import ConsentEntity, DialogDataEntity, TemporaryDialogDataEntity


def test_save_consent_should_work() -> None:
    test_base.empty_database()

    # Case True
    test_base.insert_dialog_data(dialog_id='did34')
    test_base.give_consent(has_given_consent=True, dialog_id='did34')

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
    test_base.insert_dialog_data(dialog_id='did55')
    test_base.give_consent(has_given_consent=False, dialog_id='did55')

    consents_after_two_insertions = db.query(ConsentEntity).all()
    assert len(consents_after_two_insertions) == 2

    consents_for_given_dialog_id = db.query(ConsentEntity).filter(ConsentEntity.dialog_id == 'did55').all()
    assert len(consents_for_given_dialog_id) == 1
    assert not consents_for_given_dialog_id[0].has_given_consent
    assert consents_for_given_dialog_id[0].dialog_id == 'did55'


def test_save_consent_should_throw_if_no_temporary_data_for_dialog_id() -> None:
    test_base.empty_database()
    response = test_base.give_consent(has_given_consent=True, dialog_id='did55')
    assert response.status_code == 404


def test_save_consent_should_throw_if_consent_was_already_given() -> None:
    test_base.empty_database()

    test_base.insert_dialog_data(dialog_id='did55')

    response = test_base.give_consent(has_given_consent=True, dialog_id='did55')
    assert response.status_code == 200

    response = test_base.give_consent(has_given_consent=True, dialog_id='did55')
    assert response.status_code == 409

    response = test_base.give_consent(has_given_consent=False, dialog_id='did55')
    assert response.status_code == 409


def test_save_consent_should_throw_if_invalid_payload() -> None:
    test_base.empty_database()
    test_base.insert_dialog_data(dialog_id='did55')
    response = test_base.get_test_client().post(
        '/consents/did55',
        json=''
    )
    assert response.status_code == 422

    response = test_base.get_test_client().post(
        '/consents/did55',
        json='fals'
    )
    assert response.status_code == 422

    response = test_base.get_test_client().post(
        '/consents/did55',
        json='a3sfda'
    )
    assert response.status_code == 422


def test_save_consent_should_move_data_if_consent_is_given() -> None:
    test_base.empty_database()
    db = test_base.get_database()

    test_base.insert_dialog_data(dialog_id='did55')

    assert len(db.query(ConsentEntity).all()) == 0
    assert len(db.query(TemporaryDialogDataEntity).all()) == 1
    assert len(db.query(DialogDataEntity).all()) == 0

    response = test_base.give_consent(has_given_consent=True, dialog_id='did55')
    assert response.status_code == 200

    assert len(db.query(ConsentEntity).all()) == 1
    assert len(db.query(TemporaryDialogDataEntity).all()) == 0
    assert len(db.query(DialogDataEntity).all()) == 1


def test_save_consent_should_erase_data_if_consent_is_not_given() -> None:
    test_base.empty_database()

    test_base.insert_dialog_data(dialog_id='did55')

    db = test_base.get_database()

    assert len(db.query(ConsentEntity).all()) == 0
    assert len(db.query(TemporaryDialogDataEntity).all()) == 1
    assert len(db.query(DialogDataEntity).all()) == 0

    response = test_base.give_consent(has_given_consent=False, dialog_id='did55')
    assert response.status_code == 200

    assert len(db.query(ConsentEntity).all()) == 1
    assert len(db.query(TemporaryDialogDataEntity).all()) == 0
    assert len(db.query(DialogDataEntity).all()) == 0
