"""
Pytest configuration and fixtures for the FastAPI application tests.

Provides reusable test fixtures for setting up the test client and managing
application state across test runs.
"""

import pytest
from fastapi.testclient import TestClient
from src.app import app, activities


@pytest.fixture
def client():
    """
    Fixture that provides a TestClient for making HTTP requests to the FastAPI app.
    
    This client can be used to test all endpoints in isolation.
    """
    return TestClient(app)


@pytest.fixture
def reset_activities():
    """
    Fixture that resets the activities dict to its initial state before each test.
    
    This ensures test isolation by preventing state pollution between tests.
    The fixture captures the initial state, yields control to the test, and then
    restores the original state after the test completes.
    """
    # Arrange: Save the initial state of activities
    original_activities = {
        key: {
            "description": value["description"],
            "schedule": value["schedule"],
            "max_participants": value["max_participants"],
            "participants": value["participants"].copy()
        }
        for key, value in activities.items()
    }
    
    yield
    
    # Cleanup: Restore original state after test
    activities.clear()
    activities.update(original_activities)
