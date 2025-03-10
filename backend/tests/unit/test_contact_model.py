import pytest
from app import db
from app.models.contact import Contact
from app.models.user import User
from app.models.group import Group


def test_contact_creation(app):
    """Test that a contact can be created with the expected attributes."""
    with app.app_context():
        # Create a user first
        user = User(email="test@example.com", password="password123")
        db.session.add(user)
        db.session.commit()
        
        # Create a contact
        contact = Contact(
            user_id=user.id,
            first_name="John",
            last_name="Doe",
            email="john@example.com",
            phone="123-456-7890",
            address="123 Test St",
            notes="Test notes"
        )
        db.session.add(contact)
        db.session.commit()
        
        # Retrieve the contact from the database
        retrieved_contact = Contact.query.filter_by(email="john@example.com").first()
        
        assert retrieved_contact is not None
        assert retrieved_contact.first_name == "John"
        assert retrieved_contact.last_name == "Doe"
        assert retrieved_contact.email == "john@example.com"
        assert retrieved_contact.user_id == user.id


def test_contact_to_dict(app):
    """Test the to_dict method returns the expected representation."""
    with app.app_context():
        # Create a user first
        user = User(email="test@example.com", password="password123")
        db.session.add(user)
        db.session.commit()
        
        # Create a contact
        contact = Contact(
            user_id=user.id,
            first_name="John",
            last_name="Doe",
            email="john@example.com",
            phone="123-456-7890",
            address="123 Test St",
            notes="Test notes"
        )
        db.session.add(contact)
        db.session.commit()
        
        contact_dict = contact.to_dict()
        
        assert "id" in contact_dict
        assert "user_id" in contact_dict
        assert "first_name" in contact_dict
        assert "last_name" in contact_dict
        assert "email" in contact_dict
        assert "phone" in contact_dict
        assert "address" in contact_dict
        assert "notes" in contact_dict
        assert "created_at" in contact_dict
        assert "updated_at" in contact_dict
        assert "groups" in contact_dict
        assert contact_dict["first_name"] == "John"
        assert contact_dict["last_name"] == "Doe"
        assert contact_dict["email"] == "john@example.com"


def test_contact_to_dict_simple(app, create_user):
    """Test the to_dict_simple method returns the simplified representation."""
    with app.app_context():
        # Create a user
        user = create_user()
        
        # Create a contact
        contact = Contact(
            user_id=user.id,
            first_name="John",
            last_name="Doe",
            email="john@example.com",
            phone="123-456-7890",
            address="123 Test St",
            notes="Test notes"
        )
        db.session.add(contact)
        db.session.commit()
        
        contact_dict = contact.to_dict_simple()
        
        assert "id" in contact_dict
        assert "first_name" in contact_dict
        assert "last_name" in contact_dict
        assert "email" in contact_dict
        assert "phone" in contact_dict
        
        # These should not be in the simple dict
        assert "address" not in contact_dict
        assert "notes" not in contact_dict
        assert "created_at" not in contact_dict
        assert "updated_at" not in contact_dict
        assert "groups" not in contact_dict


def test_contact_group_relationship(app):
    """Test the relationship between contacts and groups."""
    with app.app_context():
        # Create a user first
        user = User(email="test@example.com", password="password123")
        db.session.add(user)
        db.session.commit()
        
        # Create a contact
        contact = Contact(
            user_id=user.id,
            first_name="John",
            last_name="Doe",
            email="john@example.com"
        )
        db.session.add(contact)
        
        # Create groups
        group1 = Group(user_id=user.id, name="Family")
        group2 = Group(user_id=user.id, name="Work")
        db.session.add_all([group1, group2])
        db.session.commit()
        
        # Add contact to groups
        contact.groups.append(group1)
        contact.groups.append(group2)
        db.session.commit()
        
        # Test the relationships
        assert len(contact.groups) == 2
        assert group1 in contact.groups
        assert group2 in contact.groups
        
        # Test the reverse relationship
        assert contact in group1.contacts
        assert contact in group2.contacts
        
        # Test removing a group
        contact.groups.remove(group1)
        db.session.commit()
        
        assert len(contact.groups) == 1
        assert group1 not in contact.groups
        assert group2 in contact.groups 