from tests.helpers import test_base


def test_health_check() -> None:
    response = test_base.get_test_client().get('/health')
    assert response.status_code == 200
    assert response.json() == 'Ok'
