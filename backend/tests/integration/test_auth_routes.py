import pytest
import json
from app.models.user import User


def test_register_success(client):
    """Test successful user registration."""
    response = client.post(
        "/api/auth/register",
        data=json.dumps({
            "email": "new@example.com",
            "password": "password123"
        }),
        content_type="application/json"
    )
    
    assert response.status_code == 201
    data = json.loads(response.data)
    assert "message" in data
    assert "user_id" in data
    assert data["message"] == "User registered"
    
    # Check that the user was created in the database
    user = User.query.filter_by(email="new@example.com").first()
    assert user is not None
    assert user.check_password("password123")


def test_register_duplicate_email(client, create_user):
    """Test registration with an email that already exists."""
    # Create a user first
    create_user(email="existing@example.com", password="password123")
    
    # Try to register with the same email
    response = client.post(
        "/api/auth/register",
        data=json.dumps({
            "email": "existing@example.com",
            "password": "password123"
        }),
        content_type="application/json"
    )
    
    assert response.status_code == 400
    data = json.loads(response.data)
    assert "message" in data
    assert "Email already registered" in data["message"]


def test_register_missing_fields(client):
    """Test registration with missing required fields."""
    # Missing email
    response = client.post(
        "/api/auth/register",
        data=json.dumps({
            "password": "password123"
        }),
        content_type="application/json"
    )
    
    assert response.status_code == 400
    data = json.loads(response.data)
    assert "message" in data
    assert "Email and password required" in data["message"]
    
    # Missing password
    response = client.post(
        "/api/auth/register",
        data=json.dumps({
            "email": "test@example.com"
        }),
        content_type="application/json"
    )
    
    assert response.status_code == 400
    data = json.loads(response.data)
    assert "message" in data
    assert "Email and password required" in data["message"]


def test_login_success(client, create_user):
    """Test successful login."""
    # Create a user first
    create_user(email="test@example.com", password="password123")
    
    # Log in
    response = client.post(
        "/api/auth/login",
        data=json.dumps({
            "email": "test@example.com",
            "password": "password123"
        }),
        content_type="application/json"
    )
    
    assert response.status_code == 200
    data = json.loads(response.data)
    assert "access_token" in data
    assert data["access_token"] is not None


def test_login_invalid_credentials(client, create_user):
    """Test login with invalid credentials."""
    # Create a user first
    create_user(email="test@example.com", password="password123")
    
    # Try to log in with wrong password
    response = client.post(
        "/api/auth/login",
        data=json.dumps({
            "email": "test@example.com",
            "password": "wrongpassword"
        }),
        content_type="application/json"
    )
    
    assert response.status_code == 401
    data = json.loads(response.data)
    assert "message" in data
    assert "Invalid credentials" in data["message"]
    
    # Try to log in with non-existent email
    response = client.post(
        "/api/auth/login",
        data=json.dumps({
            "email": "nonexistent@example.com",
            "password": "password123"
        }),
        content_type="application/json"
    )
    
    assert response.status_code == 401
    data = json.loads(response.data)
    assert "message" in data
    assert "Invalid credentials" in data["message"]


def test_login_missing_fields(client):
    """Test login with missing required fields."""
    # Missing email
    response = client.post(
        "/api/auth/login",
        data=json.dumps({
            "password": "password123"
        }),
        content_type="application/json"
    )
    
    assert response.status_code == 400
    data = json.loads(response.data)
    assert "message" in data
    assert "Email and password required" in data["message"]
    
    # Missing password
    response = client.post(
        "/api/auth/login",
        data=json.dumps({
            "email": "test@example.com"
        }),
        content_type="application/json"
    )
    
    assert response.status_code == 400
    data = json.loads(response.data)
    assert "message" in data
    assert "Email and password required" in data["message"]


def test_get_current_user(client, auth_headers):
    """Test retrieving the current user's information."""
    # Create a user and get auth headers
    headers = auth_headers(client)
    
    # Get current user info
    response = client.get(
        "/api/auth/me",
        headers=headers
    )
    
    assert response.status_code == 200
    data = json.loads(response.data)
    assert "id" in data
    assert "email" in data
    assert "created_at" in data
    assert data["email"] == "test@example.com"


def test_get_current_user_unauthorized(client):
    """Test retrieving the current user's information without authentication."""
    response = client.get("/api/auth/me")
    
    assert response.status_code == 401
    data = json.loads(response.data)
    assert "msg" in data
    assert "Missing Authorization Header" in data["msg"]


def test_get_current_user_invalid_token(client):
    """Test retrieving the current user's information with an invalid token."""
    headers = {"Authorization": "Bearer invalid_token"}
    response = client.get(
        "/api/auth/me",
        headers=headers
    )
    
    assert response.status_code == 422  # Unprocessable Entity for invalid token 