import pytest
from unittest.mock import patch
from datetime import datetime, timezone, timedelta
from uuid import uuid4
from src.modules.meetings.model import MeetingRequest, JoinMeetingCitizenRequest
from src.core.exceptions import (
    CitizenNotFoundError,
    MeetingAlreadyScheduledError,
    MeetingNotFoundError,
    InvalidOTPError,
)


def test_create_meeting_success(testing_client, login_response):
    """Test successful meeting creation"""
    headers = {"Authorization": f"Bearer {login_response['accessToken']}"}

    meeting_data = {
        "citizenPinCode": "2DNXYD8",
        "citizenPhone": "994501234567",
        "scheduledAt": "2099-01-15T10:00:00Z",
    }

    response = testing_client.post("/meetings/", json=meeting_data, headers=headers)

    assert response.status_code == 201

    data = response.json()

    assert "id" in data
    assert data["status"] == "CREATED"


def test_create_meeting_citizen_not_found(testing_client, login_response):
    """Test meeting creation with non-existent citizen"""
    headers = {"Authorization": f"Bearer {login_response['accessToken']}"}

    meeting_data = {
        "citizenPinCode": "NONEXIST",
        "citizenPhone": "994501234567",
        "scheduledAt": "2024-01-15T10:00:00Z",
    }

    response = testing_client.post("/meetings/", json=meeting_data, headers=headers)
    assert response.status_code == 404


def test_create_meeting_already_scheduled(testing_client, login_response):
    """Test meeting creation when citizen already has a meeting"""
    headers = {"Authorization": f"Bearer {login_response['accessToken']}"}

    meeting_data = {
        "citizenPinCode": "2DNXYD8",
        "citizenPhone": "994501234567",
        "scheduledAt": "2024-01-15T10:00:00Z",
    }

    # Create first meeting
    response1 = testing_client.post("/meetings/", json=meeting_data, headers=headers)
    assert response1.status_code == 201

    # Try to create second meeting for same citizen
    response2 = testing_client.post("/meetings/", json=meeting_data, headers=headers)
    assert response2.status_code == 400  # Assuming 400 for already scheduled


def test_create_meeting_invalid_data(testing_client, login_response):
    """Test meeting creation with invalid data"""
    headers = {"Authorization": f"Bearer {login_response['accessToken']}"}

    # Invalid phone number
    invalid_data = {
        "citizenPinCode": "2DNXYD8",
        "citizenPhone": "123",  # Invalid format
        "scheduledAt": "2024-01-15T10:00:00Z",
    }

    response = testing_client.post("/meetings/", json=invalid_data, headers=headers)
    assert response.status_code == 422


def test_join_meeting_operator_success(testing_client, login_response):
    """Test operator joining a meeting"""
    headers = {"Authorization": f"Bearer {login_response['accessToken']}"}

    # First create a meeting
    meeting_data = {
        "citizenPinCode": "2DNXYD8",
        "citizenPhone": "994501234567",
        "scheduledAt": "2024-01-15T10:00:00Z",
    }

    create_response = testing_client.post(
        "/meetings/", json=meeting_data, headers=headers
    )
    assert create_response.status_code == 201

    meeting_id = create_response.json()["id"]

    # Join the meeting
    join_response = testing_client.post(
        f"/meetings/{meeting_id}/join/operator", headers=headers
    )
    assert join_response.status_code == 200

    data = join_response.json()
    assert "jitsiToken" in data


def test_join_meeting_citizen_success(testing_client, login_response):
    """Test citizen joining a meeting with valid OTP"""
    headers = {"Authorization": f"Bearer {login_response['accessToken']}"}

    # First create a meeting
    meeting_data = {
        "citizenPinCode": "2DNXYD8",
        "citizenPhone": "994501234567",
        "scheduledAt": "2024-01-15T10:00:00Z",
    }

    create_response = testing_client.post(
        "/meetings/", json=meeting_data, headers=headers
    )
    assert create_response.status_code == 201

    meeting_id = create_response.json()["id"]

    # Get OTP from Redis (you might need to mock this or access Redis directly)
    # For now, let's assume we know the OTP or mock it
    with patch("src.modules.meetings.service.generate_otp", return_value="123456"):
        # Join the meeting with OTP
        join_data = {"otp": "123456"}
        join_response = testing_client.post(
            f"/meetings/{meeting_id}/join/citizen", json=join_data
        )
        assert join_response.status_code == 200

        data = join_response.json()
        assert "jitsiToken" in data


def test_join_meeting_citizen_invalid_otp(testing_client, login_response):
    """Test citizen joining with invalid OTP"""
    headers = {"Authorization": f"Bearer {login_response['accessToken']}"}

    # First create a meeting
    meeting_data = {
        "citizenPinCode": "2DNXYD8",
        "citizenPhone": "994501234567",
        "scheduledAt": "2024-01-15T10:00:00Z",
    }

    create_response = testing_client.post(
        "/meetings/", json=meeting_data, headers=headers
    )
    assert create_response.status_code == 201

    meeting_id = create_response.json()["id"]

    # Join with invalid OTP
    join_data = {"otp": "000000"}
    join_response = testing_client.post(
        f"/meetings/{meeting_id}/join/citizen", json=join_data
    )
    assert join_response.status_code == 400  # Assuming 400 for invalid OTP


def test_join_meeting_not_found(testing_client, login_response):
    """Test joining a non-existent meeting"""
    headers = {"Authorization": f"Bearer {login_response['accessToken']}"}

    fake_meeting_id = str(uuid4())

    # Try to join non-existent meeting
    response = testing_client.post(
        f"/meetings/{fake_meeting_id}/join/operator", headers=headers
    )
    assert response.status_code == 404


def test_finish_meeting_success(testing_client, login_response):
    """Test finishing a meeting"""
    headers = {"Authorization": f"Bearer {login_response['accessToken']}"}

    # First create a meeting
    meeting_data = {
        "citizenPinCode": "2DNXYD8",
        "citizenPhone": "994501234567",
        "scheduledAt": "2024-01-15T10:00:00Z",
    }

    create_response = testing_client.post(
        "/meetings/", json=meeting_data, headers=headers
    )
    assert create_response.status_code == 201

    meeting_id = create_response.json()["id"]

    # Finish the meeting
    finish_response = testing_client.post(
        f"/meetings/{meeting_id}/finish", headers=headers
    )
    assert finish_response.status_code == 204


def test_finish_meeting_not_found(testing_client, login_response):
    """Test finishing a non-existent meeting"""
    headers = {"Authorization": f"Bearer {login_response['accessToken']}"}

    fake_meeting_id = str(uuid4())

    # Try to finish non-existent meeting
    response = testing_client.post(
        f"/meetings/{fake_meeting_id}/finish", headers=headers
    )
    assert response.status_code == 404


def test_meeting_redis_caching(testing_client, login_response, redis_client):
    """Test that meeting data is properly cached in Redis"""
    headers = {"Authorization": f"Bearer {login_response['accessToken']}"}

    meeting_data = {
        "citizenPinCode": "2DNXYD8",
        "citizenPhone": "994501234567",
        "scheduledAt": "2024-01-15T10:00:00Z",
    }

    # Create meeting
    response = testing_client.post("/meetings/", json=meeting_data, headers=headers)
    assert response.status_code == 201

    meeting_id = response.json()["id"]

    # Check that meeting data was cached in Redis
    cached_data = redis_client.get(f"meeting:{meeting_id}")
    assert cached_data is not None

    # Verify the cached data contains OTP and citizen data
    import json

    meeting_redis_data = json.loads(cached_data)
    assert "otp" in meeting_redis_data
    assert "citizen_data" in meeting_redis_data
