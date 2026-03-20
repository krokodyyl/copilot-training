"""
Unit tests for the FastAPI activities API endpoints.

Tests cover all three endpoints:
- GET /activities
- POST /activities/{activity_name}/signup
- POST /activities/{activity_name}/unregister

All tests follow the AAA (Arrange-Act-Assert) pattern for clarity.
"""

import pytest
from src.app import activities


class TestGetActivities:
    """Tests for the GET /activities endpoint."""
    
    def test_get_activities_returns_all_activities(self, client, reset_activities):
        """
        Arrange: Use the test client and fresh activities state from fixtures
        Act: Send a GET request to /activities
        Assert: Verify all 9 activities are returned with correct structure
        """
        # Act
        response = client.get("/activities")
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        
        # Check that all 9 activities are present
        assert len(data) == 9
        assert "Chess Club" in data
        assert "Programming Class" in data
        assert "Gym Class" in data
        assert "Basketball Team" in data
        assert "Tennis Club" in data
        assert "Art Studio" in data
        assert "Music Band" in data
        assert "Science Club" in data
        assert "Debate Team" in data
    
    def test_get_activities_response_structure(self, client, reset_activities):
        """
        Arrange: Use the test client and fresh activities state
        Act: Send a GET request to /activities
        Assert: Verify each activity has the correct schema
        """
        # Act
        response = client.get("/activities")
        data = response.json()
        
        # Assert - Verify structure of one activity as representative
        chess_club = data.get("Chess Club")
        assert chess_club is not None
        assert "description" in chess_club
        assert "schedule" in chess_club
        assert "max_participants" in chess_club
        assert "participants" in chess_club
        assert isinstance(chess_club["participants"], list)
    
    def test_get_activities_contains_initial_participants(self, client, reset_activities):
        """
        Arrange: Use the test client and fresh activities state
        Act: Send a GET request to /activities
        Assert: Verify initial participants are present in the activities
        """
        # Act
        response = client.get("/activities")
        data = response.json()
        
        # Assert
        chess_club_participants = data["Chess Club"]["participants"]
        assert "michael@mergington.edu" in chess_club_participants
        assert "daniel@mergington.edu" in chess_club_participants
        assert len(chess_club_participants) == 2


class TestSignupEndpoint:
    """Tests for the POST /activities/{activity_name}/signup endpoint."""
    
    def test_signup_new_student_success(self, client, reset_activities):
        """
        Arrange: Use the test client and fresh activities state; identify a new student email
        Act: Send a POST request to signup for an activity
        Assert: Verify student is added to participants and response is correct
        """
        # Arrange
        activity_name = "Chess Club"
        new_email = "new_student@mergington.edu"
        initial_count = len(activities[activity_name]["participants"])
        
        # Act
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": new_email}
        )
        
        # Assert
        assert response.status_code == 200
        assert response.json() == {
            "message": f"Signed up {new_email} for {activity_name}"
        }
        assert new_email in activities[activity_name]["participants"]
        assert len(activities[activity_name]["participants"]) == initial_count + 1
    
    def test_signup_duplicate_student_returns_400(self, client, reset_activities):
        """
        Arrange: Use the test client and fresh activities state with an existing student
        Act: Try to signup a student who is already signed up
        Assert: Verify 400 error is returned and state is unchanged
        """
        # Arrange
        activity_name = "Chess Club"
        existing_email = "michael@mergington.edu"
        initial_count = len(activities[activity_name]["participants"])
        
        # Act
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": existing_email}
        )
        
        # Assert
        assert response.status_code == 400
        assert response.json()["detail"] == "Student already signed up for this activity"
        assert len(activities[activity_name]["participants"]) == initial_count
    
    def test_signup_nonexistent_activity_returns_404(self, client, reset_activities):
        """
        Arrange: Use the test client and fresh activities state; use invalid activity name
        Act: Try to signup for a non-existent activity
        Assert: Verify 404 error is returned
        """
        # Arrange
        invalid_activity = "Nonexistent Activity"
        email = "student@mergington.edu"
        
        # Act
        response = client.post(
            f"/activities/{invalid_activity}/signup",
            params={"email": email}
        )
        
        # Assert
        assert response.status_code == 404
        assert response.json()["detail"] == "Activity not found"
    
    def test_signup_multiple_activities_same_student(self, client, reset_activities):
        """
        Arrange: Use the test client and fresh activities state
        Act: Signup the same student for multiple different activities
        Assert: Verify student is added to all activities
        """
        # Arrange
        email = "multi_activity@mergington.edu"
        activities_to_join = ["Chess Club", "Programming Class", "Tennis Club"]
        
        # Act & Assert for each activity
        for activity_name in activities_to_join:
            response = client.post(
                f"/activities/{activity_name}/signup",
                params={"email": email}
            )
            assert response.status_code == 200
            assert email in activities[activity_name]["participants"]


class TestUnregisterEndpoint:
    """Tests for the POST /activities/{activity_name}/unregister endpoint."""
    
    def test_unregister_existing_student_success(self, client, reset_activities):
        """
        Arrange: Use the test client and fresh activities state with an existing student
        Act: Send a POST request to unregister a student
        Assert: Verify student is removed from participants and response is correct
        """
        # Arrange
        activity_name = "Chess Club"
        existing_email = "michael@mergington.edu"
        initial_count = len(activities[activity_name]["participants"])
        assert existing_email in activities[activity_name]["participants"]
        
        # Act
        response = client.post(
            f"/activities/{activity_name}/unregister",
            params={"email": existing_email}
        )
        
        # Assert
        assert response.status_code == 200
        assert response.json() == {
            "message": f"Unregistered {existing_email} from {activity_name}"
        }
        assert existing_email not in activities[activity_name]["participants"]
        assert len(activities[activity_name]["participants"]) == initial_count - 1
    
    def test_unregister_nonexistent_student_returns_400(self, client, reset_activities):
        """
        Arrange: Use the test client and fresh activities state; use non-participant email
        Act: Try to unregister a student who is not signed up
        Assert: Verify 400 error is returned and state is unchanged
        """
        # Arrange
        activity_name = "Chess Club"
        not_registered_email = "not_registered@mergington.edu"
        initial_count = len(activities[activity_name]["participants"])
        
        # Act
        response = client.post(
            f"/activities/{activity_name}/unregister",
            params={"email": not_registered_email}
        )
        
        # Assert
        assert response.status_code == 400
        assert response.json()["detail"] == "Student not signed up for this activity"
        assert len(activities[activity_name]["participants"]) == initial_count
    
    def test_unregister_nonexistent_activity_returns_404(self, client, reset_activities):
        """
        Arrange: Use the test client and fresh activities state; use invalid activity name
        Act: Try to unregister from a non-existent activity
        Assert: Verify 404 error is returned
        """
        # Arrange
        invalid_activity = "Nonexistent Activity"
        email = "student@mergington.edu"
        
        # Act
        response = client.post(
            f"/activities/{invalid_activity}/unregister",
            params={"email": email}
        )
        
        # Assert
        assert response.status_code == 404
        assert response.json()["detail"] == "Activity not found"
    
    def test_unregister_then_signup_again(self, client, reset_activities):
        """
        Arrange: Use the test client and fresh activities state
        Act: Unregister a student, then sign them up again
        Assert: Verify student can be re-added after being removed
        """
        # Arrange
        activity_name = "Chess Club"
        email = "michael@mergington.edu"
        
        # Act & Assert: First unregister
        response = client.post(
            f"/activities/{activity_name}/unregister",
            params={"email": email}
        )
        assert response.status_code == 200
        assert email not in activities[activity_name]["participants"]
        
        # Act & Assert: Then signup again
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )
        assert response.status_code == 200
        assert email in activities[activity_name]["participants"]
