import time
from typing import List

import pytest
from tests.helpers import test_base

from app.config.config import settings
from app.data.entities import ConsentEntity, DialogDataEntity, TemporaryDialogDataEntity


def test_save_data_should_work() -> None:
    test_base.empty_database()
    payload = test_base.get_test_payloads_save_dialog_data()[0]

    response = test_base.insert_dialog_data(payload=payload, dialog_id='did34', customer_id='id12')

    assert response.status_code == 200
    response_json = response.json()
    assert response_json['text'] == payload['text']
    assert response_json['language'] == payload['language'].lower()
    assert response_json['customer_id'] == 'id12'
    assert response_json['dialog_id'] == 'did34'
    assert response_json['received_at_timestamp_utc'] is not None
    assert response_json['id'] == 1

    db = test_base.get_database()
    assert len(db.query(ConsentEntity).all()) == 0
    assert len(db.query(TemporaryDialogDataEntity).all()) == 1
    assert len(db.query(DialogDataEntity).all()) == 0
    saved_item = db.query(TemporaryDialogDataEntity).first()
    assert saved_item.customer_id == 'id12'
    assert saved_item.dialog_id == 'did34'


def test_save_data_multiple_requests_should_work() -> None:
    test_base.empty_database()
    ids: List[int] = []
    for i in range(10):
        payload = {
            'text': f'Can you help me? {i}',
            'language': 'EN'
        }

        response = test_base.insert_dialog_data(payload=payload, customer_id='id12', dialog_id='did34')
        assert response.status_code == 200

        response_json = response.json()
        assert response_json['text'] == f'Can you help me? {i}'
        assert response_json['language'] == 'en'
        assert response_json['customer_id'] == 'id12'
        assert response_json['dialog_id'] == 'did34'
        assert response_json['received_at_timestamp_utc'] is not None
        item_id = response_json['id']
        assert item_id not in ids
        assert item_id == i + 1

        db = test_base.get_database()
        assert len(db.query(ConsentEntity).all()) == 0
        assert len(db.query(TemporaryDialogDataEntity).all()) == i + 1
        assert len(db.query(DialogDataEntity).all()) == 0


def test_save_data_should_return_unprocessable_entity_if_invalid_body() -> None:
    test_base.empty_database()
    payload = {
        'text': 'Good afternoon chatbot'
    }
    response = test_base.insert_dialog_data(payload=payload, customer_id='id13', dialog_id='did35')
    assert response.status_code == 422


def test_save_data_should_return_unprocessable_entity_if_no_body() -> None:
    response = test_base.get_test_client().post(
        '/data/id13/did35',
    )
    assert response.status_code == 422


def test_save_data_missing_path_param_should_return_not_found() -> None:
    response = test_base.get_test_client().post(
        '/data/id12',
        json={
            'text': 'Good afternoon chatbot',
            'language': 'en'
        }
    )
    assert response.status_code == 404


def test_get_data_should_work_without_filters() -> None:
    test_base.empty_database()
    dialog_data_payloads = test_base.get_test_payloads_save_dialog_data()

    test_base.insert_dialog_data(payload=dialog_data_payloads[0], customer_id='id89', dialog_id='did878')
    test_base.insert_dialog_data(payload=dialog_data_payloads[1], customer_id='id89', dialog_id='did878')
    test_base.insert_dialog_data(payload=dialog_data_payloads[2], customer_id='id11', dialog_id='did3')

    test_base.give_consent(has_given_consent=True, dialog_id='did878')

    get_data = test_base.get_test_client().get(
        '/data'
    )

    get_data_json = get_data.json()

    assert len(get_data_json) == 2
    for index, payload in enumerate(dialog_data_payloads):
        assert payload['text'] == dialog_data_payloads[index]['text']
        assert payload['language'].lower() == dialog_data_payloads[index]['language'].lower()


def test_get_data_should_return_results_in_descending_order() -> None:
    test_base.empty_database()
    dialog_data_payloads = test_base.get_test_payloads_save_dialog_data()

    test_base.insert_dialog_data(payload=dialog_data_payloads[0], customer_id='id89', dialog_id='did878')
    test_base.insert_dialog_data(payload=dialog_data_payloads[1], customer_id='id89', dialog_id='did878')
    test_base.insert_dialog_data(payload=dialog_data_payloads[2], customer_id='id11', dialog_id='did3')
    test_base.insert_dialog_data(payload=dialog_data_payloads[1], customer_id='id11', dialog_id='did3')

    test_base.give_consent(has_given_consent=True, dialog_id='did878')
    test_base.give_consent(has_given_consent=True, dialog_id='did3')

    get_data = test_base.get_dialog_data(query_string='')

    get_data_json = get_data.json()

    assert len(get_data_json) == 4

    expected_order = [{
        'text': dialog_data_payloads[1]['text'],
        'customer_id': 'id11',
        'dialog_id': 'did3'
    }, {
        'text': dialog_data_payloads[2]['text'],
        'customer_id': 'id11',
        'dialog_id': 'did3'
    }, {
        'text': dialog_data_payloads[1]['text'],
        'customer_id': 'id89',
        'dialog_id': 'did878'
    }, {
        'text': dialog_data_payloads[0]['text'],
        'customer_id': 'id89',
        'dialog_id': 'did878'
    }]

    for index, result in enumerate(get_data_json):
        expected_order_item = expected_order[index]
        assert result['text'] == expected_order_item['text']
        assert result['customer_id'] == expected_order_item['customer_id']
        assert result['dialog_id'] == expected_order_item['dialog_id']


def test_get_data_should_not_return_temporary_data() -> None:
    test_base.empty_database()
    dialog_data_payloads = test_base.get_test_payloads_save_dialog_data()

    test_base.insert_dialog_data(payload=dialog_data_payloads[0], customer_id='id11', dialog_id='did3')
    test_base.insert_dialog_data(payload=dialog_data_payloads[1], customer_id='id89', dialog_id='did878')
    test_base.insert_dialog_data(payload=dialog_data_payloads[2], customer_id='id89', dialog_id='did878')

    get_data = test_base.get_dialog_data(query_string='')

    get_data_json = get_data.json()
    assert len(get_data_json) == 0


def test_get_data_should_work_with_customer_filter() -> None:
    test_base.empty_database()
    dialog_data_payloads = test_base.get_test_payloads_save_dialog_data()

    test_base.insert_dialog_data(payload=dialog_data_payloads[0], customer_id='id11', dialog_id='did3')
    test_base.insert_dialog_data(payload=dialog_data_payloads[1], customer_id='id89', dialog_id='did12')
    test_base.insert_dialog_data(payload=dialog_data_payloads[2], customer_id='id89', dialog_id='did12')

    test_base.give_consent(has_given_consent=True, dialog_id='did12')
    get_data = test_base.get_dialog_data(query_string='?customerId=id89')
    get_data_json = get_data.json()
    assert len(get_data_json) == 2


def test_get_data_should_work_with_language_filter() -> None:
    test_base.empty_database()
    dialog_data_payloads = test_base.get_test_payloads_save_dialog_data()

    test_base.insert_dialog_data(payload=dialog_data_payloads[0], customer_id='id89', dialog_id='did12')
    test_base.insert_dialog_data(payload=dialog_data_payloads[1], customer_id='id89', dialog_id='did12')
    test_base.insert_dialog_data(
        payload={
            'text': 'Bonjour!',
            'language': 'FR'
        },
        customer_id='id89',
        dialog_id='did12'
    )

    test_base.give_consent(has_given_consent=True, dialog_id='did12')
    get_data = test_base.get_dialog_data(query_string='?language=fr')
    get_data_json = get_data.json()
    assert len(get_data_json) == 1


def test_get_data_should_work_with_multiple_filters() -> None:
    test_base.empty_database()
    dialog_data_payloads = test_base.get_test_payloads_save_dialog_data()

    test_base.insert_dialog_data(payload=dialog_data_payloads[0], customer_id='id11', dialog_id='did3')
    test_base.insert_dialog_data(payload=dialog_data_payloads[1], customer_id='id89', dialog_id='did12')
    test_base.insert_dialog_data(
        payload={
            'text': 'Bonjour!',
            'language': 'FR'
        },
        customer_id='id89',
        dialog_id='did12'
    )

    test_base.give_consent(has_given_consent=True, dialog_id='did12')

    get_data_fr_id89 = test_base.get_dialog_data(query_string='?language=fr&customerId=id89')

    get_data_fr_id89_json = get_data_fr_id89.json()
    assert len(get_data_fr_id89_json) == 1

    get_data_en_id89 = test_base.get_dialog_data(query_string='?language=en&customerId=id89')

    get_data_en_id89_json = get_data_en_id89.json()
    assert len(get_data_en_id89_json) == 1


def test_get_data_should_work_if_filter_does_not_match_data() -> None:
    test_base.empty_database()
    dialog_data_payloads = test_base.get_test_payloads_save_dialog_data()

    test_base.insert_dialog_data(payload=dialog_data_payloads[0], customer_id='id11', dialog_id='did3')
    test_base.insert_dialog_data(payload=dialog_data_payloads[1], customer_id='id89', dialog_id='did12')
    test_base.insert_dialog_data(payload=dialog_data_payloads[2], customer_id='id89', dialog_id='did878')

    test_base.give_consent(has_given_consent=True, dialog_id='did12')

    get_data_unknown_language = test_base.get_dialog_data(query_string='?language=unknown')
    get_data_unknown_language_json = get_data_unknown_language.json()
    assert len(get_data_unknown_language_json) == 0

    get_data_unknown_customer_id = test_base.get_dialog_data(query_string='?customerId=unknown')
    get_data_unknown_customer_id_json = get_data_unknown_customer_id.json()
    assert len(get_data_unknown_customer_id_json) == 0

    get_data_no_results = test_base.get_dialog_data(query_string='?language=unknown&customerId=unknown')
    get_data_no_results_json = get_data_no_results.json()
    assert len(get_data_no_results_json) == 0


def test_get_data_should_work_if_database_is_empty() -> None:
    test_base.empty_database()
    get_data_no_results = test_base.get_dialog_data(query_string='?language=unknown&customerId=unknown')
    get_data_no_results_json = get_data_no_results.json()
    assert get_data_no_results.status_code == 200
    assert len(get_data_no_results_json) == 0


def test_get_data_should_not_be_case_sensitive() -> None:
    test_base.empty_database()
    dialog_data_payloads = test_base.get_test_payloads_save_dialog_data()

    test_base.insert_dialog_data(payload=dialog_data_payloads[0], customer_id='id11', dialog_id='did3')
    test_base.insert_dialog_data(payload=dialog_data_payloads[1], customer_id='id89', dialog_id='did12')
    test_base.insert_dialog_data(
        payload={
            'text': 'Bonjour!',
            'language': 'FR'
        },
        customer_id='id89',
        dialog_id='did12'
    )

    test_base.give_consent(has_given_consent=True, dialog_id='did12')

    get_data = test_base.get_dialog_data(query_string='?language=fr')
    get_data_json = get_data.json()
    assert len(get_data_json) == 1

    get_data2 = test_base.get_dialog_data(query_string='?language=Fr')
    get_data2_json = get_data2.json()
    assert len(get_data2_json) == 1

    get_data3 = test_base.get_dialog_data(query_string='?language=fR')
    get_data3_json = get_data3.json()
    assert len(get_data3_json) == 1

    get_data4 = test_base.get_dialog_data(query_string='?language=FR')
    get_data4_json = get_data4.json()
    assert len(get_data4_json) == 1


def test_get_data_skip_and_limit_should_work() -> None:
    test_base.empty_database()
    dialog_data_payloads = test_base.get_test_payloads_save_dialog_data()

    for _ in range(100):
        test_base.insert_dialog_data(payload=dialog_data_payloads[0], customer_id='id11', dialog_id='did3')
        test_base.insert_dialog_data(payload=dialog_data_payloads[1], customer_id='id89', dialog_id='did12')

    test_base.give_consent(has_given_consent=True, dialog_id='did3')
    test_base.give_consent(has_given_consent=True, dialog_id='did12')

    get_all_data = test_base.get_dialog_data(query_string='')
    get_all_data_json = get_all_data.json()
    assert len(get_all_data_json) == 200

    get_all_data_skip_zero = test_base.get_dialog_data(query_string='?skip=0')
    get_all_data_skip_zero_json = get_all_data_skip_zero.json()
    assert len(get_all_data_skip_zero_json) == 200

    get_data_skip = test_base.get_dialog_data(query_string='?skip=12')
    get_data_skip_json = get_data_skip.json()
    assert len(get_data_skip_json) == 188

    get_data_limit = test_base.get_dialog_data(query_string='?limit=19')
    get_data_limit_json = get_data_limit.json()
    assert len(get_data_limit_json) == 19

    get_data_skip_and_limit = test_base.get_dialog_data(query_string='?skip=198&limit=19')
    get_data_skip_and_limit_json = get_data_skip_and_limit.json()
    assert len(get_data_skip_and_limit_json) == 2

    get_data_skip_more_than_total_entries = test_base.get_dialog_data(query_string='?skip=500')
    get_data_skip_more_than_total_entries_json = get_data_skip_more_than_total_entries.json()
    assert len(get_data_skip_more_than_total_entries_json) == 0

    get_data_limit_more_than_total_entries = test_base.get_dialog_data(query_string='?limit=500')
    get_data_limit_more_than_total_entries_json = get_data_limit_more_than_total_entries.json()
    assert len(get_data_limit_more_than_total_entries_json) == 200


def test_get_data_skip_and_limit_should_throw() -> None:
    test_base.empty_database()
    dialog_data_payloads = test_base.get_test_payloads_save_dialog_data()

    test_base.insert_dialog_data(payload=dialog_data_payloads[0], customer_id='id11', dialog_id='did3')
    test_base.insert_dialog_data(payload=dialog_data_payloads[1], customer_id='id89', dialog_id='did12')

    test_base.give_consent(has_given_consent=True, dialog_id='did3')
    test_base.give_consent(has_given_consent=True, dialog_id='did12')

    get_data_incorrect_skip = test_base.get_dialog_data(query_string='?skip=-3')
    assert get_data_incorrect_skip.status_code == 422

    get_data_incorrect_limit = test_base.get_dialog_data(query_string='?limit=0')
    assert get_data_incorrect_limit.status_code == 422


def test_get_anomalies_should_work() -> None:
    settings.ANOMALY_PERIOD_MS = 500
    test_base.empty_database()
    dialog_data_payloads = test_base.get_test_payloads_save_dialog_data()

    test_base.insert_dialog_data(payload=dialog_data_payloads[0], customer_id='id11', dialog_id='did3')

    get_data_no_anomaly = test_base.get_test_client().get('/data/anomaly')
    get_data_no_anomaly_json = get_data_no_anomaly.json()
    assert len(get_data_no_anomaly_json) == 0

    time.sleep(0.8)

    get_data_anomaly = test_base.get_test_client().get('/data/anomaly')
    get_data_anomaly_json = get_data_anomaly.json()
    assert len(get_data_anomaly_json) == 1
    assert get_data_anomaly_json[0]['customer_id'] == 'id11'
    assert get_data_anomaly_json[0]['dialog_id'] == 'did3'


def test_get_anomalies_should_not_throw_with_empty_database() -> None:
    settings.ANOMALY_PERIOD_MS = 800
    test_base.empty_database()

    get_data_no_anomaly = test_base.get_test_client().get('/data/anomaly')
    get_data_no_anomaly_json = get_data_no_anomaly.json()
    assert len(get_data_no_anomaly_json) == 0
    assert get_data_no_anomaly.status_code == 200


def test_get_anomalies_work_if_there_are_no_anomalies() -> None:
    settings.ANOMALY_PERIOD_MS = 36000000
    test_base.empty_database()
    dialog_data_payloads = test_base.get_test_payloads_save_dialog_data()

    test_base.insert_dialog_data(payload=dialog_data_payloads[0], customer_id='id11', dialog_id='did3')

    get_data_no_anomaly = test_base.get_test_client().get('/data/anomaly')
    get_data_no_anomaly_json = get_data_no_anomaly.json()
    assert len(get_data_no_anomaly_json) == 0
    assert get_data_no_anomaly.status_code == 200


@pytest.fixture(scope='session', autouse=True)
def cleanup(request: pytest.FixtureRequest) -> None:
    def clean_test_db() -> None:
        test_base.remove_test_database()
    request.addfinalizer(clean_test_db)
