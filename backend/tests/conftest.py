import pytest
import os
import sys
import json
from flask import Flask
from flask_jwt_extended import JWTManager

# Add the root directory to the Python path so we can import the app modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# Import the app factory and db
from app import create_app, db, jwt
from tests.config import TestConfig

@pytest.fixture
def app():
    """Create and configure a Flask app for testing."""
    app = Flask(__name__)
    app.config.from_object(TestConfig)
    
    # Initialize extensions with app
    db.init_app(app)
    jwt.init_app(app)
    
    # Register blueprints
    from app.routes.auth import auth_bp
    from app.routes.contacts import contacts_bp
    from app.routes.groups import groups_bp
    
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(contacts_bp, url_prefix='/api/contacts')
    app.register_blueprint(groups_bp, url_prefix='/api/groups')
    
    # Establish an application context
    with app.app_context():
        # Create all tables in the database
        db.create_all()
        yield app
        # Clean up the database
        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app):
    """A test client for the app."""
    return app.test_client()


@pytest.fixture
def auth_headers():
    """Function to generate authentication headers with JWT token."""
    def _auth_headers(client, email="test@example.com", password="password"):
        # First, create a user if it doesn't exist
        from app.models.user import User
        
        with client.application.app_context():
            if not User.query.filter_by(email=email).first():
                user = User(email=email, password=password)
                db.session.add(user)
                db.session.commit()
        
        # Log in to get the token
        response = client.post(
            "/api/auth/login", 
            json={"email": email, "password": password},
            content_type="application/json"
        )
        data = json.loads(response.data)
        token = data.get("access_token")
        
        return {"Authorization": f"Bearer {token}"}
    
    return _auth_headers


@pytest.fixture
def create_user():
    """Function to create a test user."""
    def _create_user(email="test@example.com", password="password"):
        from app.models.user import User
        
        user = User(email=email, password=password)
        db.session.add(user)
        db.session.commit()
        return user
    
    return _create_user


@pytest.fixture
def create_contact():
    """Function to create a test contact."""
    def _create_contact(user_id, first_name="John", last_name="Doe", email="john@example.com", 
                       phone="123-456-7890", address="123 Test St", notes="Test notes"):
        from app.models.contact import Contact
        
        contact = Contact(
            user_id=user_id,
            first_name=first_name,
            last_name=last_name,
            email=email,
            phone=phone,
            address=address,
            notes=notes
        )
        db.session.add(contact)
        db.session.commit()
        return contact
    
    return _create_contact


@pytest.fixture
def create_group():
    """Function to create a test group."""
    def _create_group(user_id, name="Test Group"):
        from app.models.group import Group
        
        group = Group(
            user_id=user_id,
            name=name
        )
        db.session.add(group)
        db.session.commit()
        return group
    
    return _create_group 