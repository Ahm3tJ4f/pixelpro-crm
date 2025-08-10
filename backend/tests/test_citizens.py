from src.core.domain.citizen import CitizenDomain
from datetime import datetime, timezone

from src.core.enums import RedisKeys
from src.core.redis import get_redis_value
from src.modules.citizens.model import CitizenResponse


def test_get_citizen(testing_client, login_response):

    headers = {"Authorization": f"Bearer {login_response['accessToken']}"}

    response = testing_client.get("/citizens/2DNXYD8", headers=headers)

    assert response.status_code == 200

    # data = CitizenDomain.model_validate(**response.json())
    data = response.json()

    assert data["pinCode"] == "2DNXYD8"
    assert data["firstName"] == "Ahmad"
    assert data["lastName"] == "Jafarov"
    assert data["patronymic"] == "Roman"
    assert data["documentNumber"] == "AA1234567"
    assert data["addressLine"] == "Azerbaijan, Baku"

    parsed_date = datetime.fromisoformat(data["dateOfBirth"].replace("Z", "+00:00"))
    expected_date = datetime(2002, 3, 12, tzinfo=timezone.utc)
    assert parsed_date == expected_date


def test_get_citizen_invalid_pin(testing_client, login_response):
    headers = {"Authorization": f"Bearer {login_response['accessToken']}"}

    invalid_pins = ["ABCD12", "ABCD1234", "ABCD12I", "ABCD12O"]
    for pin in invalid_pins:
        response = testing_client.get(f"/citizens/{pin}", headers=headers)
        assert response.status_code == 422


def test_get_citizen_not_found(testing_client, login_response):
    headers = {"Authorization": f"Bearer {login_response['accessToken']}"}

    response = testing_client.get("/citizens/ABC1234", headers=headers)
    assert response.status_code == 404


def test_get_citizen_redis_caching(testing_client, login_response, redis_client):
    headers = {"Authorization": f"Bearer {login_response['accessToken']}"}

    # Clear cache
    redis_client.delete("citizen:2dnxyd8")

    # Verify cache is empty
    cached_data = redis_client.get("citizen:2dnxyd8")
    assert cached_data is None

    response1 = testing_client.get("/citizens/2DNXYD8", headers=headers)
    assert response1.status_code == 200

    cached_data = redis_client.get("citizen:2dnxyd8")
    assert cached_data is not None
