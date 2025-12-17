"""Tests for the Mergington High School Activities API"""
import pytest


class TestRootEndpoint:
    """Test the root endpoint"""

    def test_root_redirect(self, client):
        """Test that the root endpoint redirects to the static HTML page"""
        response = client.get("/", follow_redirects=False)
        assert response.status_code == 307
        assert response.headers["location"] == "/static/index.html"


class TestActivitiesEndpoint:
    """Test the activities endpoint"""

    def test_get_activities_returns_all_activities(self, client):
        """Test that the /activities endpoint returns all activities"""
        response = client.get("/activities")
        assert response.status_code == 200
        
        activities = response.json()
        assert isinstance(activities, dict)
        assert len(activities) > 0
        
        # Check that all expected activities are present
        expected_activities = [
            "Chess Club",
            "Programming Class",
            "Gym Class",
            "Basketball Team",
            "Soccer Club",
            "Art Club",
            "Drama Club",
            "Debate Team",
            "Math Club"
        ]
        for activity in expected_activities:
            assert activity in activities

    def test_get_activities_structure(self, client):
        """Test that each activity has the correct structure"""
        response = client.get("/activities")
        activities = response.json()
        
        for name, details in activities.items():
            assert "description" in details
            assert "schedule" in details
            assert "max_participants" in details
            assert "participants" in details
            assert isinstance(details["participants"], list)


class TestSignupEndpoint:
    """Test the signup endpoint"""

    def test_signup_for_activity(self, client):
        """Test successful signup for an activity"""
        email = "testuser@mergington.edu"
        activity = "Chess Club"
        
        response = client.post(
            f"/activities/{activity}/signup",
            params={"email": email}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert email in data["message"]
        assert activity in data["message"]

    def test_signup_duplicate_email(self, client):
        """Test that duplicate signup returns an error"""
        email = "michael@mergington.edu"  # Already signed up for Chess Club
        activity = "Chess Club"
        
        response = client.post(
            f"/activities/{activity}/signup",
            params={"email": email}
        )
        
        assert response.status_code == 400
        data = response.json()
        assert "detail" in data
        assert "already signed up" in data["detail"]

    def test_signup_nonexistent_activity(self, client):
        """Test signup for a non-existent activity"""
        email = "testuser@mergington.edu"
        activity = "Nonexistent Club"
        
        response = client.post(
            f"/activities/{activity}/signup",
            params={"email": email}
        )
        
        assert response.status_code == 404
        data = response.json()
        assert "detail" in data
        assert "not found" in data["detail"]

    def test_signup_adds_participant_to_activity(self, client):
        """Test that signup actually adds the participant to the activity"""
        email = "newuser@mergington.edu"
        activity = "Soccer Club"
        
        # Get initial participant count
        response = client.get("/activities")
        initial_count = len(response.json()[activity]["participants"])
        
        # Sign up
        response = client.post(
            f"/activities/{activity}/signup",
            params={"email": email}
        )
        assert response.status_code == 200
        
        # Verify participant was added
        response = client.get("/activities")
        updated_count = len(response.json()[activity]["participants"])
        assert updated_count == initial_count + 1
        assert email in response.json()[activity]["participants"]


class TestRemoveParticipantEndpoint:
    """Test the remove participant endpoint"""

    def test_remove_participant(self, client):
        """Test successful removal of a participant"""
        email = "michael@mergington.edu"
        activity = "Chess Club"
        
        response = client.delete(
            f"/activities/{activity}/participants/{email}"
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert email in data["message"]
        assert activity in data["message"]

    def test_remove_nonexistent_participant(self, client):
        """Test removal of a non-existent participant"""
        email = "nonexistent@mergington.edu"
        activity = "Chess Club"
        
        response = client.delete(
            f"/activities/{activity}/participants/{email}"
        )
        
        assert response.status_code == 400
        data = response.json()
        assert "detail" in data
        assert "not signed up" in data["detail"]

    def test_remove_participant_from_nonexistent_activity(self, client):
        """Test removal from a non-existent activity"""
        email = "testuser@mergington.edu"
        activity = "Nonexistent Club"
        
        response = client.delete(
            f"/activities/{activity}/participants/{email}"
        )
        
        assert response.status_code == 404
        data = response.json()
        assert "detail" in data
        assert "not found" in data["detail"]

    def test_remove_participant_actually_removes(self, client):
        """Test that removal actually removes the participant"""
        email = "daniel@mergington.edu"
        activity = "Chess Club"
        
        # Verify participant is signed up
        response = client.get("/activities")
        assert email in response.json()[activity]["participants"]
        
        # Remove participant
        response = client.delete(
            f"/activities/{activity}/participants/{email}"
        )
        assert response.status_code == 200
        
        # Verify participant was removed
        response = client.get("/activities")
        assert email not in response.json()[activity]["participants"]


class TestIntegration:
    """Integration tests for the API"""

    def test_signup_and_remove_flow(self, client):
        """Test the complete flow of signing up and removing a participant"""
        email = "integration@mergington.edu"
        activity = "Art Club"
        
        # Sign up
        response = client.post(
            f"/activities/{activity}/signup",
            params={"email": email}
        )
        assert response.status_code == 200
        
        # Verify signed up
        response = client.get("/activities")
        assert email in response.json()[activity]["participants"]
        
        # Remove
        response = client.delete(
            f"/activities/{activity}/participants/{email}"
        )
        assert response.status_code == 200
        
        # Verify removed
        response = client.get("/activities")
        assert email not in response.json()[activity]["participants"]

    def test_multiple_signups(self, client):
        """Test multiple signups for the same activity"""
        activity = "Drama Club"
        emails = [
            "drama1@mergington.edu",
            "drama2@mergington.edu",
            "drama3@mergington.edu"
        ]
        
        # Sign up multiple users
        for email in emails:
            response = client.post(
                f"/activities/{activity}/signup",
                params={"email": email}
            )
            assert response.status_code == 200
        
        # Verify all are signed up
        response = client.get("/activities")
        participants = response.json()[activity]["participants"]
        for email in emails:
            assert email in participants
