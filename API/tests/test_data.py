from typing import List

import pytest
from tests.helpers import test_base, test_client


def test_save_data_should_work() -> None:
    response = test_client.post(
        '/data/id12/did34',
        json={
            'text': 'Good afternoon chatbot',
            'language': 'EN'
        }
    )
    assert response.status_code == 200
    response_json = response.json()
    assert response_json['text'] == 'Good afternoon chatbot'
    assert response_json['language'] == 'EN'
    assert response_json['customer_id'] == 'id12'
    assert response_json['dialog_id'] == 'did34'
    assert response_json['received_at_timestamp_utc'] is not None
    assert response_json['id'] >= 1


def test_save_data_multiple_requests_should_work() -> None:
    ids: List[int] = []
    for i in range(10):
        response = test_client.post(
            '/data/id12/did34',
            json={
                'text': f'Can you help me? {i}',
                'language': 'EN'
            }
        )
        assert response.status_code == 200
        response_json = response.json()
        assert response_json['text'] == f'Can you help me? {i}'
        assert response_json['language'] == 'EN'
        assert response_json['customer_id'] == 'id12'
        assert response_json['dialog_id'] == 'did34'
        assert response_json['received_at_timestamp_utc'] is not None
        id = response_json['id']
        assert id not in ids


def test_save_data_should_return_unprocessable_entity_if_invalid_body() -> None:
    response = test_client.post(
        '/data/id13/did35',
        json={
            'text': 'Good afternoon chatbot'
        }
    )
    assert response.status_code == 422


def test_save_data_should_return_unprocessable_entity_if_no_body() -> None:
    response = test_client.post(
        '/data/id13/did35',
    )
    assert response.status_code == 422


def test_save_data_missing_path_param_should_fail() -> None:
    response = test_client.post(
        '/data/id12',
        json={
            'text': 'Good afternoon chatbot',
            'language': 'EN'
        }
    )
    assert response.status_code == 404


@pytest.fixture(scope='session', autouse=True)
def cleanup(request: pytest.FixtureRequest) -> None:
    def clean_test_db() -> None:
        test_base.remove_test_database()
    request.addfinalizer(clean_test_db)
