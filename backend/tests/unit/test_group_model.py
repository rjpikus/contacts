import pytest
from app import db
from app.models.group import Group
from app.models.user import User
from app.models.contact import Contact


def test_group_creation(app):
    """Test that a group can be created with the expected attributes."""
    with app.app_context():
        # Create a user first
        user = User(email="test@example.com", password="password123")
        db.session.add(user)
        db.session.commit()
        
        # Create a group
        group = Group(
            user_id=user.id,
            name="Test Group"
        )
        db.session.add(group)
        db.session.commit()
        
        # Retrieve the group from the database
        retrieved_group = Group.query.filter_by(name="Test Group").first()
        
        assert retrieved_group is not None
        assert retrieved_group.name == "Test Group"
        assert retrieved_group.user_id == user.id


def test_group_to_dict(app):
    """Test the to_dict method returns the expected representation."""
    with app.app_context():
        # Create a user first
        user = User(email="test@example.com", password="password123")
        db.session.add(user)
        db.session.commit()
        
        # Create a group
        group = Group(
            user_id=user.id,
            name="Test Group"
        )
        db.session.add(group)
        db.session.commit()
        
        group_dict = group.to_dict()
        
        assert "id" in group_dict
        assert "user_id" in group_dict
        assert "name" in group_dict
        assert "contacts_count" in group_dict
        assert group_dict["name"] == "Test Group"
        assert group_dict["user_id"] == user.id
        assert group_dict["contacts_count"] == 0


def test_group_to_dict_simple(app, create_user):
    """Test the to_dict_simple method returns the simplified representation."""
    with app.app_context():
        # Create a user
        user = create_user()
        
        # Create a group
        group = Group(
            user_id=user.id,
            name="Family"
        )
        db.session.add(group)
        db.session.commit()
        
        group_dict = group.to_dict_simple()
        
        assert "id" in group_dict
        assert "name" in group_dict
        
        # These should not be in the simple dict
        assert "user_id" not in group_dict
        assert "contacts_count" not in group_dict
        
        assert group_dict["name"] == "Family"


def test_group_contact_relationship(app):
    """Test the relationship between groups and contacts."""
    with app.app_context():
        # Create a user first
        user = User(email="test@example.com", password="password123")
        db.session.add(user)
        db.session.commit()
        
        # Create a group
        group = Group(
            user_id=user.id,
            name="Test Group"
        )
        db.session.add(group)
        
        # Create contacts
        contact1 = Contact(
            user_id=user.id,
            first_name="John",
            last_name="Doe",
            email="john@example.com"
        )
        contact2 = Contact(
            user_id=user.id,
            first_name="Jane",
            last_name="Smith",
            email="jane@example.com"
        )
        db.session.add_all([contact1, contact2])
        db.session.commit()
        
        # Add contacts to the group
        group.contacts.append(contact1)
        group.contacts.append(contact2)
        db.session.commit()
        
        # Test the relationships
        assert len(group.contacts) == 2
        assert contact1 in group.contacts
        assert contact2 in group.contacts
        
        # Test the reverse relationship
        assert group in contact1.groups
        assert group in contact2.groups
        
        # Test removing a contact
        group.contacts.remove(contact1)
        db.session.commit()
        
        assert len(group.contacts) == 1
        assert contact1 not in group.contacts
        assert contact2 in group.contacts
        
        # Test the to_dict method with contacts
        group_dict = group.to_dict()
        assert group_dict["contacts_count"] == 1 