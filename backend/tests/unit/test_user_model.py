import pytest
from app import db
from app.models.user import User


def test_user_creation(app):
    """Test that a user can be created with the expected attributes."""
    with app.app_context():
        user = User(email="test@example.com", password="password123")
        db.session.add(user)
        db.session.commit()
        
        # Retrieve the user from the database
        retrieved_user = User.query.filter_by(email="test@example.com").first()
        
        assert retrieved_user is not None
        assert retrieved_user.email == "test@example.com"
        assert retrieved_user.password != "password123"  # Password should be hashed


def test_password_hashing(app):
    """Test that passwords are properly hashed and can be verified."""
    with app.app_context():
        user = User(email="test@example.com", password="password123")
        
        # Check that the password is hashed
        assert user.password != "password123"
        
        # Check that the password can be verified
        assert user.check_password("password123") is True
        assert user.check_password("wrongpassword") is False


def test_user_to_dict(app):
    """Test the to_dict method returns the expected representation."""
    with app.app_context():
        user = User(email="test@example.com", password="password123")
        db.session.add(user)
        db.session.commit()
        
        user_dict = user.to_dict()
        
        assert "id" in user_dict
        assert "email" in user_dict
        assert "created_at" in user_dict
        assert "password" not in user_dict  # Password should not be included
        assert user_dict["email"] == "test@example.com"


def test_user_relationships(app, create_contact, create_group):
    """Test the relationships between users, contacts, and groups."""
    with app.app_context():
        # Create a user
        user = User(email="test@example.com", password="password123")
        db.session.add(user)
        db.session.commit()
        
        # Create contacts and groups for the user
        contact1 = create_contact(user.id, first_name="John", last_name="Doe")
        contact2 = create_contact(user.id, first_name="Jane", last_name="Smith")
        
        group1 = create_group(user.id, name="Family")
        group2 = create_group(user.id, name="Work")
        
        # Test the relationships
        assert len(user.contacts) == 2
        assert len(user.groups) == 2
        
        # Test that deleting the user cascades to contacts and groups
        db.session.delete(user)
        db.session.commit()
        
        # Check that contacts and groups were deleted
        from app.models.contact import Contact
        from app.models.group import Group
        
        assert Contact.query.filter_by(user_id=user.id).count() == 0
        assert Group.query.filter_by(user_id=user.id).count() == 0 