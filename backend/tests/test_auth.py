def test_register_user(testing_client):
    payload = {
        "username": "testuser",
        "password": "testpassword",
        "firstName": "Test",
        "lastName": "User",
        "userRole": "ADMIN",
    }
    response = testing_client.post("/auth/register", json=payload)

    assert response.status_code == 200

    data = response.json()
    assert data["accessToken"]
    assert data["refreshToken"]


def test_login_user(login_response):
    assert login_response["accessToken"]
    assert login_response["refreshToken"]


def test_refresh_token(testing_client, login_response):

    payload = {"refreshToken": login_response["refreshToken"]}

    response = testing_client.post("/auth/refresh", json=payload)

    assert response.status_code == 200

    data = response.json()

    assert data["accessToken"]
    assert data["refreshToken"]


def test_logout_user(testing_client, login_response):
    access_token = login_response["accessToken"]

    headers = {"Authorization": f"Bearer {access_token}"}

    response = testing_client.post("/auth/logout", headers=headers)

    assert response.status_code == 204


def test_refresh_token_security_flow(testing_client, login_response):

    initial_refresh_token = login_response["refreshToken"]

    refresh_payload = {"refreshToken": initial_refresh_token}
    refresh_response = testing_client.post("/auth/refresh", json=refresh_payload)

    assert refresh_response.status_code == 200

    login_payload = {"username": "testuser", "password": "testpassword"}

    new_login_response = testing_client.post("/auth/login", json=login_payload)

    assert new_login_response.status_code == 200

    payload = {"refreshToken": refresh_response.json()["refreshToken"]}

    invalid_token_response = testing_client.post("/auth/refresh", json=payload)

    assert invalid_token_response.status_code == 401

    headers = {"Authorization": f"Bearer {new_login_response.json()['accessToken']}"}

    logout_response = testing_client.post("/auth/logout", headers=headers)

    assert logout_response.status_code == 204
