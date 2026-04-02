
import pytest
from fastapi.testclient import TestClient
from fastapi import HTTPException
from src.app import app, activities, get_activity, validate_not_signed_up, validate_signed_up



def test_get_activities():
    # Arrange
    client = TestClient(app)
    # Act
    response = client.get("/activities")
    # Assert
    assert response.status_code == 200
    assert isinstance(response.json(), dict)
    assert "Chess Club" in response.json()



def test_signup_for_activity_success():
    # Arrange
    test_email = "nuevo@mergington.edu"
    activity_name = "Chess Club"
    activities[activity_name]["participants"] = ["michael@mergington.edu"]  # Reset
    client = TestClient(app)
    # Act
    response = client.post(f"/activities/{activity_name}/signup", params={"email": test_email})
    # Assert
    assert response.status_code == 200
    assert test_email in activities[activity_name]["participants"]
    assert response.json()["message"] == f"Signed up {test_email} for {activity_name}"



def test_signup_for_activity_already_signed_up():
    # Arrange
    test_email = "michael@mergington.edu"
    activity_name = "Chess Club"
    activities[activity_name]["participants"] = [test_email]
    client = TestClient(app)
    # Act
    response = client.post(f"/activities/{activity_name}/signup", params={"email": test_email})
    # Assert
    assert response.status_code == 400
    assert response.json()["detail"] == "Student already signed up for this activity"



def test_signup_for_activity_not_found():
    # Arrange
    test_email = "nuevo@mergington.edu"
    activity_name = "NoExiste"
    client = TestClient(app)
    # Act
    response = client.post(f"/activities/{activity_name}/signup", params={"email": test_email})
    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"



def test_remove_participant_success():
    # Arrange
    test_email = "michael@mergington.edu"
    activity_name = "Chess Club"
    activities[activity_name]["participants"] = [test_email]
    client = TestClient(app)
    # Act
    response = client.delete(f"/activities/{activity_name}/signup", params={"email": test_email})
    # Assert
    assert response.status_code == 200
    assert test_email not in activities[activity_name]["participants"]
    assert response.json()["message"] == f"Removed {test_email} from {activity_name}"



def test_remove_participant_not_found():
    # Arrange
    test_email = "noesta@mergington.edu"
    activity_name = "Chess Club"
    activities[activity_name]["participants"] = []
    client = TestClient(app)
    # Act
    response = client.delete(f"/activities/{activity_name}/signup", params={"email": test_email})
    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Participant not found in this activity"



def test_remove_participant_activity_not_found():
    # Arrange
    test_email = "alguien@mergington.edu"
    activity_name = "NoExiste"
    client = TestClient(app)
    # Act
    response = client.delete(f"/activities/{activity_name}/signup", params={"email": test_email})
    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"

# --- Pruebas unitarias para helpers internos ---
def test_get_activity_found():
    # Arrange
    activity_name = "Chess Club"
    # Act
    result = get_activity(activity_name)
    # Assert
    assert result is activities[activity_name]

def test_get_activity_not_found():
    # Arrange
    activity_name = "NoExiste"
    # Act & Assert
    with pytest.raises(HTTPException) as exc:
        get_activity(activity_name)
    assert exc.value.status_code == 404
    assert exc.value.detail == "Activity not found"

def test_validate_not_signed_up_ok():
    # Arrange
    activity = {"participants": ["a@b.com"]}
    email = "nuevo@b.com"
    # Act & Assert
    validate_not_signed_up(activity, email)  # No excepción

def test_validate_not_signed_up_error():
    # Arrange
    activity = {"participants": ["a@b.com"]}
    email = "a@b.com"
    # Act & Assert
    with pytest.raises(HTTPException) as exc:
        validate_not_signed_up(activity, email)
    assert exc.value.status_code == 400
    assert exc.value.detail == "Student already signed up for this activity"

def test_validate_signed_up_ok():
    # Arrange
    activity = {"participants": ["a@b.com"]}
    email = "a@b.com"
    # Act & Assert
    validate_signed_up(activity, email)  # No excepción

def test_validate_signed_up_error():
    # Arrange
    activity = {"participants": ["a@b.com"]}
    email = "otro@b.com"
    # Act & Assert
    with pytest.raises(HTTPException) as exc:
        validate_signed_up(activity, email)
    assert exc.value.status_code == 404
    assert exc.value.detail == "Participant not found in this activity"
