import pytest
from fastapi.testclient import TestClient
from src.app import app

client = TestClient(app)

def test_root_redirects_to_index():
    response = client.get("/")
    assert response.status_code == 200
    # TestClient follows redirects, so we should get the HTML content
    assert "<!DOCTYPE html>" in str(response.content)
    assert "Mergington High School" in str(response.content)

def test_get_activities():
    response = client.get("/activities")
    assert response.status_code == 200
    activities = response.json()
    
    # Check if we have activities
    assert len(activities) > 0
    
    # Check if each activity has the required fields
    for activity_name, details in activities.items():
        assert isinstance(activity_name, str)
        assert "description" in details
        assert "schedule" in details
        assert "max_participants" in details
        assert "participants" in details
        assert isinstance(details["max_participants"], int)
        assert isinstance(details["participants"], list)

def test_signup_for_activity():
    # Test successful signup
    response = client.post("/activities/Chess Club/signup?email=test@mergington.edu")
    assert response.status_code == 200
    assert response.json()["message"] == "Signed up test@mergington.edu for Chess Club"
    
    # Verify the participant was added
    activities = client.get("/activities").json()
    assert "test@mergington.edu" in activities["Chess Club"]["participants"]

def test_signup_duplicate():
    # First signup
    client.post("/activities/Programming Class/signup?email=duplicate@mergington.edu")
    
    # Try to signup again
    response = client.post("/activities/Programming Class/signup?email=duplicate@mergington.edu")
    assert response.status_code == 400
    assert "already signed up" in response.json()["detail"].lower()

def test_signup_nonexistent_activity():
    response = client.post("/activities/NonexistentClub/signup?email=test@mergington.edu")
    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()

def test_unregister_from_activity():
    # First sign up a test user
    test_email = "unregister_test@mergington.edu"
    test_activity = "Art Club"
    
    client.post(f"/activities/{test_activity}/signup?email={test_email}")
    
    # Now unregister
    response = client.delete(f"/activities/{test_activity}/unregister?email={test_email}")
    assert response.status_code == 200
    assert f"Unregistered {test_email} from {test_activity}" in response.json()["message"]
    
    # Verify the participant was removed
    activities = client.get("/activities").json()
    assert test_email not in activities[test_activity]["participants"]

def test_unregister_not_registered():
    response = client.delete("/activities/Chess Club/unregister?email=notregistered@mergington.edu")
    assert response.status_code == 400
    assert "not registered" in response.json()["detail"].lower()

def test_unregister_nonexistent_activity():
    response = client.delete("/activities/NonexistentClub/unregister?email=test@mergington.edu")
    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()