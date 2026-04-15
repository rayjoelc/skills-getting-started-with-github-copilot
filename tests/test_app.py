"""
Tests for Mergington High School Activities API

Using Arrange-Act-Assert (AAA) pattern for test structure.
"""

import pytest
from fastapi.testclient import TestClient
from src.app import app


@pytest.fixture
def client():
    """Arrange: Create a test client for the FastAPI app"""
    return TestClient(app)


class TestGetActivities:
    """Tests for GET /activities endpoint"""

    def test_get_activities_returns_all_activities(self, client):
        """Arrange: Activities are pre-populated in app.py"""
        # Act: Call the endpoint
        response = client.get("/activities")

        # Assert: Verify response
        assert response.status_code == 200
        activities = response.json()
        assert len(activities) == 9
        assert "Chess Club" in activities
        assert "Programming Class" in activities

    def test_get_activities_response_structure(self, client):
        """Arrange: Call the activities endpoint"""
        # Act: Get activities
        response = client.get("/activities")

        # Assert: Each activity has required fields
        activities = response.json()
        for activity_name, details in activities.items():
            assert isinstance(activity_name, str)
            assert "description" in details
            assert "schedule" in details
            assert "max_participants" in details
            assert "participants" in details
            assert isinstance(details["participants"], list)


class TestSignup:
    """Tests for POST /activities/{activity_name}/signup endpoint"""

    def test_signup_success(self, client):
        """Arrange: Select an activity and email to sign up"""
        activity_name = "Chess Club"
        email = "newstudent@mergington.edu"

        # Act: Sign up for activity
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )

        # Assert: Signup successful
        assert response.status_code == 200
        assert email in response.json()["message"]
        
        # Assert: Participant added to activity
        activities = client.get("/activities").json()
        assert email in activities[activity_name]["participants"]

    def test_signup_duplicate_email(self, client):
        """Arrange: Sign up a student once"""
        activity_name = "Programming Class"
        email = "emma@mergington.edu"  # Already enrolled

        # Act: Try to sign up the same student again
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )

        # Assert: Duplicate signup is rejected
        assert response.status_code == 400
        assert "already signed up" in response.json()["detail"]

    def test_signup_activity_not_found(self, client):
        """Arrange: Use a non-existent activity name"""
        activity_name = "Nonexistent Club"
        email = "student@mergington.edu"

        # Act: Try to sign up for missing activity
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )

        # Assert: 404 error returned
        assert response.status_code == 404
        assert "not found" in response.json()["detail"]


class TestUnregister:
    """Tests for POST /activities/{activity_name}/unregister endpoint"""

    def test_unregister_success(self, client):
        """Arrange: Add a new participant, then remove them"""
        activity_name = "Art Studio"
        email = "teststudent@mergington.edu"

        # First, sign up
        client.post(f"/activities/{activity_name}/signup", params={"email": email})

        # Act: Unregister the student
        response = client.post(
            f"/activities/{activity_name}/unregister",
            params={"email": email}
        )

        # Assert: Unregister successful
        assert response.status_code == 200
        assert email in response.json()["message"]
        
        # Assert: Participant removed from activity
        activities = client.get("/activities").json()
        assert email not in activities[activity_name]["participants"]

    def test_unregister_student_not_enrolled(self, client):
        """Arrange: Use email that's not enrolled in activity"""
        activity_name = "Robotics Club"
        email = "notstudent@mergington.edu"

        # Act: Try to unregister a non-enrolled student
        response = client.post(
            f"/activities/{activity_name}/unregister",
            params={"email": email}
        )

        # Assert: 400 error returned
        assert response.status_code == 400
        assert "not signed up" in response.json()["detail"]

    def test_unregister_activity_not_found(self, client):
        """Arrange: Use a non-existent activity name"""
        activity_name = "Fake Activity"
        email = "student@mergington.edu"

        # Act: Try to unregister from missing activity
        response = client.post(
            f"/activities/{activity_name}/unregister",
            params={"email": email}
        )

        # Assert: 404 error returned
        assert response.status_code == 404
        assert "not found" in response.json()["detail"]


class TestEdgeCases:
    """Tests for edge cases and special scenarios"""

    def test_url_encoded_activity_name(self, client):
        """Arrange: Activity names with spaces need URL encoding"""
        activity_name = "Programming Class"
        email = "test@mergington.edu"

        # Act: Sign up using URL-encoded activity name
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )

        # Assert: Signup works with spaces in name
        assert response.status_code == 200

    def test_case_sensitive_activity_name(self, client):
        """Arrange: Activity names are case-sensitive"""
        # Act: Try wrong case
        response = client.post(
            "/activities/chess%20club/signup",  # lowercase
            params={"email": "test@mergington.edu"}
        )

        # Assert: Returns 404 (exact name required)
        assert response.status_code == 404
