"""
Tests for the Mergington High School API
"""

import pytest
from fastapi.testclient import TestClient
import sys
from pathlib import Path

# Add the src directory to the path so we can import app
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from app import app


@pytest.fixture
def client():
    """Create a test client for the FastAPI app"""
    return TestClient(app)


@pytest.fixture
def reset_activities():
    """Reset activities to initial state before each test"""
    from app import activities
    # Store initial state
    initial_state = {
        "Basketball Team": {
            "description": "Join the basketball team and compete in local tournaments",
            "leader": "Coach Smith",
            "schedule": "Mondays and Wednesdays, 4:00 PM - 6:00 PM",
            "max_participants": 15,
            "participants": []
        },
        "Soccer Club": {
            "description": "Practice soccer skills and participate in matches",
            "leader": "Coach Lee",
            "schedule": "Tuesdays and Thursdays, 4:00 PM - 6:00 PM",
            "max_participants": 20,
            "participants": []
        },
        "Art Club": {
            "description": "Explore various art techniques and create projects",
            "leader": "Ms. Davis",
            "schedule": "Fridays, 3:00 PM - 5:00 PM",
            "max_participants": 10,
            "participants": []
        },
        "Drama Club": {
            "description": "Participate in theater productions and improve acting skills",
            "leader": "Mr. Brown",
            "schedule": "Thursdays, 3:30 PM - 5:30 PM",
            "max_participants": 15,
            "participants": []
        },
        "Debate Team": {
            "description": "Engage in debates and develop public speaking skills",
            "leader": "Ms. Wilson",
            "schedule": "Wednesdays, 4:00 PM - 5:30 PM",
            "max_participants": 12,
            "participants": []
        },
        "Math Club": {
            "description": "Solve challenging math problems and participate in competitions",
            "leader": "Mr. Taylor",
            "schedule": "Tuesdays, 3:00 PM - 4:30 PM",
            "max_participants": 20,
            "participants": []
        },
        "Chess Club": {
            "description": "Learn strategies and compete in chess tournaments",
            "leader": "Mr. Johnson",
            "schedule": "Fridays, 3:30 PM - 5:00 PM",
            "max_participants": 12,
            "participants": ["michael@mergington.edu", "daniel@mergington.edu"]
        },
        "Programming Class": {
            "description": "Learn programming fundamentals and build software projects",
            "schedule": "Tuesdays and Thursdays, 3:30 PM - 4:30 PM",
            "max_participants": 20,
            "participants": ["emma@mergington.edu", "sophia@mergington.edu"]
        },
        "Gym Class": {
            "description": "Physical education and sports activities",
            "schedule": "Mondays, Wednesdays, Fridays, 2:00 PM - 3:00 PM",
            "max_participants": 30,
            "participants": ["john@mergington.edu", "olivia@mergington.edu"]
        }
    }
    
    # Clear current activities and restore initial state
    activities.clear()
    activities.update(initial_state)
    
    yield
    
    # Reset after test
    activities.clear()
    activities.update(initial_state)


class TestRoot:
    """Tests for the root endpoint"""
    
    def test_root_redirect(self, client):
        """Test that root redirects to static/index.html"""
        response = client.get("/", follow_redirects=False)
        assert response.status_code == 307
        assert response.headers["location"] == "/static/index.html"


class TestGetActivities:
    """Tests for the get_activities endpoint"""
    
    def test_get_all_activities(self, client, reset_activities):
        """Test retrieving all activities"""
        response = client.get("/activities")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, dict)
        assert "Basketball Team" in data
        assert "Soccer Club" in data
        assert "Art Club" in data
        assert len(data) == 9
    
    def test_activity_structure(self, client, reset_activities):
        """Test that activities have the correct structure"""
        response = client.get("/activities")
        data = response.json()
        activity = data["Basketball Team"]
        
        assert "description" in activity
        assert "leader" in activity
        assert "schedule" in activity
        assert "max_participants" in activity
        assert "participants" in activity
        assert isinstance(activity["participants"], list)
    
    def test_existing_participants(self, client, reset_activities):
        """Test that existing participants are returned"""
        response = client.get("/activities")
        data = response.json()
        
        # Chess Club should have 2 participants
        assert len(data["Chess Club"]["participants"]) == 2
        assert "michael@mergington.edu" in data["Chess Club"]["participants"]
        
        # Programming Class should have 2 participants
        assert len(data["Programming Class"]["participants"]) == 2


class TestSignup:
    """Tests for the signup endpoint"""
    
    def test_successful_signup(self, client, reset_activities):
        """Test successful signup for an activity"""
        response = client.post(
            "/activities/Basketball Team/signup",
            params={"email": "john@school.edu"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "Signed up john@school.edu for Basketball Team"
    
    def test_signup_appears_in_activity(self, client, reset_activities):
        """Test that signup appears in activity participants"""
        client.post(
            "/activities/Art Club/signup",
            params={"email": "student@school.edu"}
        )
        
        response = client.get("/activities")
        data = response.json()
        assert "student@school.edu" in data["Art Club"]["participants"]
    
    def test_signup_nonexistent_activity(self, client, reset_activities):
        """Test signup for activity that doesn't exist"""
        response = client.post(
            "/activities/Nonexistent Club/signup",
            params={"email": "john@school.edu"}
        )
        assert response.status_code == 404
        data = response.json()
        assert data["detail"] == "Activity not found"
    
    def test_duplicate_signup(self, client, reset_activities):
        """Test that a student cannot sign up twice for the same activity"""
        # First signup
        client.post(
            "/activities/Basketball Team/signup",
            params={"email": "john@school.edu"}
        )
        
        # Try to signup again
        response = client.post(
            "/activities/Basketball Team/signup",
            params={"email": "john@school.edu"}
        )
        assert response.status_code == 400
        data = response.json()
        assert data["detail"] == "Student already signed up for this activity"
    
    def test_multiple_students_signup(self, client, reset_activities):
        """Test multiple different students can signup for same activity"""
        client.post("/activities/Soccer Club/signup", params={"email": "student1@school.edu"})
        client.post("/activities/Soccer Club/signup", params={"email": "student2@school.edu"})
        client.post("/activities/Soccer Club/signup", params={"email": "student3@school.edu"})
        
        response = client.get("/activities")
        data = response.json()
        participants = data["Soccer Club"]["participants"]
        
        assert len(participants) == 3
        assert "student1@school.edu" in participants
        assert "student2@school.edu" in participants
        assert "student3@school.edu" in participants


class TestUnregister:
    """Tests for the unregister endpoint"""
    
    def test_successful_unregister(self, client, reset_activities):
        """Test successful unregister from an activity"""
        # First signup
        client.post(
            "/activities/Basketball Team/signup",
            params={"email": "john@school.edu"}
        )
        
        # Then unregister
        response = client.delete(
            "/activities/Basketball Team/unregister",
            params={"email": "john@school.edu"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "Unregistered john@school.edu from Basketball Team"
    
    def test_unregister_appears_in_activity(self, client, reset_activities):
        """Test that unregister removes from activity participants"""
        # Signup and then unregister from Chess Club (which has initial participants)
        client.delete(
            "/activities/Chess Club/unregister",
            params={"email": "michael@mergington.edu"}
        )
        
        response = client.get("/activities")
        data = response.json()
        assert "michael@mergington.edu" not in data["Chess Club"]["participants"]
        assert len(data["Chess Club"]["participants"]) == 1
    
    def test_unregister_nonexistent_activity(self, client, reset_activities):
        """Test unregister from activity that doesn't exist"""
        response = client.delete(
            "/activities/Nonexistent Club/unregister",
            params={"email": "john@school.edu"}
        )
        assert response.status_code == 404
        data = response.json()
        assert data["detail"] == "Activity not found"
    
    def test_unregister_not_registered(self, client, reset_activities):
        """Test unregister when student is not registered"""
        response = client.delete(
            "/activities/Basketball Team/unregister",
            params={"email": "notregistered@school.edu"}
        )
        assert response.status_code == 400
        data = response.json()
        assert data["detail"] == "Student is not registered for this activity"
    
    def test_signup_and_unregister_cycle(self, client, reset_activities):
        """Test that student can signup and unregister multiple times"""
        email = "test@school.edu"
        
        # Signup
        client.post("/activities/Drama Club/signup", params={"email": email})
        response = client.get("/activities")
        assert email in response.json()["Drama Club"]["participants"]
        
        # Unregister
        client.delete("/activities/Drama Club/unregister", params={"email": email})
        response = client.get("/activities")
        assert email not in response.json()["Drama Club"]["participants"]
        
        # Signup again
        client.post("/activities/Drama Club/signup", params={"email": email})
        response = client.get("/activities")
        assert email in response.json()["Drama Club"]["participants"]
