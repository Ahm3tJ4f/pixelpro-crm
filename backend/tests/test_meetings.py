from datetime import datetime, timedelta, timezone
import json


def test_create_meeting(testing_client, login_response, redis_client):
    # Get access token from login
    access_token = login_response["accessToken"]  # camelCase
    headers = {"Authorization": f"Bearer {access_token}"}

    # Step 1: Get a specific citizen by pin_code
    # You need to know a valid pin_code first - let's use a test one
    test_pin_code = "2DnXyD8"  # Use a valid test pin_code

    citizens_response = testing_client.get(
        f"/citizens/{test_pin_code}", headers=headers
    )
    assert citizens_response.status_code == 200

    citizen_data = citizens_response.json()
    assert citizen_data["pinCode"] == test_pin_code.upper()

    # Step 2: Create dynamic meeting payload with tomorrow's date
    tomorrow = datetime.now(timezone.utc) + timedelta(days=1)
    meeting_payload = {
        "citizenPinCode": test_pin_code,  # camelCase
        "citizenPhone": "994501234567",  # camelCase
        "scheduledAt": tomorrow.isoformat().replace("+00:00", "Z"),  # Clean conversion
    }

    meeting_response = testing_client.post(
        "/meetings", json=meeting_payload, headers=headers
    )

    # Assertions
    assert meeting_response.status_code == 201

    meeting_data = meeting_response.json()
    assert meeting_data["id"] is not None
    assert meeting_data["status"] == "CREATED"
    assert meeting_data["firstName"] == citizen_data["firstName"]  # camelCase
    assert meeting_data["lastName"] == citizen_data["lastName"]  # camelCase
    assert meeting_data["pinCode"] == test_pin_code.upper()  # camelCase
    assert meeting_data["phone"] == meeting_payload["citizenPhone"]  # camelCase
    assert meeting_data["scheduledAt"] == meeting_payload["scheduledAt"]  # camelCase

    # Step 3: Check if meeting record exists in Redis
    meeting_id = str(meeting_data["id"])
    redis_key = f"meeting:{meeting_id}"

    meeting_redis_data = redis_client.get(redis_key)
    assert (
        meeting_redis_data is not None
    ), f"Meeting data not found in Redis with key: {redis_key}"


def test_create_duplicate_meeting(testing_client, login_response):
    # Get access token from login
    access_token = login_response["accessToken"]
    headers = {"Authorization": f"Bearer {access_token}"}

    # Step 1: Get a citizen to use
    test_pin_code = "2DnXyD8"
    citizens_response = testing_client.get(
        f"/citizens/{test_pin_code}", headers=headers
    )
    assert citizens_response.status_code == 200

    citizen_data = citizens_response.json()
    assert citizen_data["pinCode"] == test_pin_code.upper()

    # Step 2: Try to create duplicate meeting (should fail with 409)
    tomorrow = datetime.now(timezone.utc) + timedelta(days=1)
    meeting_payload = {
        "citizenPinCode": test_pin_code,
        "citizenPhone": "994501234567",
        "scheduledAt": tomorrow.isoformat().replace("+00:00", "Z"),
    }

    duplicate_meeting_response = testing_client.post(
        "/meetings", json=meeting_payload, headers=headers
    )

    # Should fail with 409 Conflict
    assert duplicate_meeting_response.status_code == 409


# def test_join_meeting_operator(testing_client, login_response, redis_client):
#     # Get access token from login
#     access_token = login_response["accessToken"]
#     headers = {"Authorization": f"Bearer {access_token}"}

#     # Step 1: Create a meeting first (use same citizen)
#     test_pin_code = "2DnXyD8"
#     tomorrow = datetime.now(timezone.utc) + timedelta(days=1)
#     meeting_payload = {
#         "citizenPinCode": test_pin_code,
#         "citizenPhone": "994501234567",
#         "scheduledAt": tomorrow.isoformat().replace("+00:00", "Z"),
#     }

#     meeting_response = testing_client.post(
#         "/meetings", json=meeting_payload, headers=headers
#     )
#     assert meeting_response.status_code == 201

#     meeting_data = meeting_response.json()
#     meeting_id = meeting_data["id"]

#     # Step 2: Operator joins the meeting (status: CREATED → PENDING)
#     join_response = testing_client.post(
#         f"/meetings/{meeting_id}/join-operator", headers=headers
#     )
#     assert join_response.status_code == 200

#     join_data = join_response.json()
#     assert "jitsiToken" in join_data

#     # Step 3: Verify meeting status changed to PENDING
#     meetings_response = testing_client.get("/meetings", headers=headers)
#     assert meetings_response.status_code == 200

#     meetings = meetings_response.json()
#     updated_meeting = next(m for m in meetings if m["id"] == meeting_id)
#     assert updated_meeting["status"] == "PENDING"


# def test_join_meeting_citizen(testing_client, login_response, redis_client):
#     # Get access token for operator (needed to create meeting)
#     access_token = login_response["accessToken"]
#     operator_headers = {"Authorization": f"Bearer {access_token}"}

#     # Step 1: Create a meeting first (operator action) - use same citizen
#     test_pin_code = "2DnXyD8"
#     tomorrow = datetime.now(timezone.utc) + timedelta(days=1)
#     meeting_payload = {
#         "citizenPinCode": test_pin_code,
#         "citizenPhone": "994501234567",
#         "scheduledAt": tomorrow.isoformat().replace("+00:00", "Z"),
#     }

#     meeting_response = testing_client.post(
#         "/meetings", json=meeting_payload, headers=operator_headers
#     )
#     assert meeting_response.status_code == 201

#     meeting_data = meeting_response.json()
#     meeting_id = meeting_data["id"]

#     # Step 2: Operator joins first (status: CREATED → PENDING)
#     testing_client.post(
#         f"/meetings/{meeting_id}/join-operator", headers=operator_headers
#     )

#     # Step 3: Get OTP from Redis
#     redis_key = f"meeting:{meeting_id}"
#     meeting_redis_data = redis_client.get(redis_key)
#     assert meeting_redis_data is not None

#     import json

#     redis_meeting = json.loads(meeting_redis_data)
#     otp = redis_meeting["otp"]

#     # Step 4: Citizen joins with OTP (NO AUTH NEEDED)
#     citizen_join_payload = {"otp": otp}
#     join_response = testing_client.post(
#         f"/meetings/{meeting_id}/join-citizen",
#         json=citizen_join_payload,
#         # No headers - citizen doesn't need authentication
#     )
#     assert join_response.status_code == 200

#     join_data = join_response.json()
#     assert "jitsiToken" in join_data

#     # Step 5: Verify meeting status changed to IN_PROGRESS
#     meetings_response = testing_client.get("/meetings", headers=operator_headers)
#     assert meetings_response.status_code == 200

#     meetings = meetings_response.json()
#     updated_meeting = next(m for m in meetings if m["id"] == meeting_id)
#     assert updated_meeting["status"] == "IN_PROGRESS"
