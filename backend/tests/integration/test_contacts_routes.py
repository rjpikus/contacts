import pytest
import json
import io
from app.models.contact import Contact


def test_get_contacts_empty(client, auth_headers):
    """Test getting all contacts when there are none."""
    headers = auth_headers(client)
    
    response = client.get(
        "/api/contacts",
        headers=headers
    )
    
    assert response.status_code == 200
    data = json.loads(response.data)
    assert "contacts" in data
    assert isinstance(data["contacts"], list)
    assert len(data["contacts"]) == 0


def test_get_contacts(client, auth_headers, create_user, create_contact):
    """Test getting all contacts."""
    # Create a user and get auth headers
    user = create_user()
    headers = auth_headers(client)
    
    # Create some contacts
    create_contact(user.id, first_name="John", last_name="Doe")
    create_contact(user.id, first_name="Jane", last_name="Smith")
    
    # Get contacts
    response = client.get(
        "/api/contacts",
        headers=headers
    )
    
    assert response.status_code == 200
    data = json.loads(response.data)
    assert "contacts" in data
    assert isinstance(data["contacts"], list)
    assert len(data["contacts"]) == 2
    
    # Check the contacts data
    assert any(c["first_name"] == "John" and c["last_name"] == "Doe" for c in data["contacts"])
    assert any(c["first_name"] == "Jane" and c["last_name"] == "Smith" for c in data["contacts"])


def test_get_contacts_search(client, auth_headers, create_user, create_contact):
    """Test getting contacts with search filter."""
    # Create a user and get auth headers
    user = create_user()
    headers = auth_headers(client)
    
    # Create some contacts
    create_contact(user.id, first_name="John", last_name="Doe")
    create_contact(user.id, first_name="Jane", last_name="Smith")
    create_contact(user.id, first_name="Bob", last_name="Johnson")
    
    # Search for contacts containing "Jo"
    response = client.get(
        "/api/contacts?search=Jo",
        headers=headers
    )
    
    assert response.status_code == 200
    data = json.loads(response.data)
    assert "contacts" in data
    assert isinstance(data["contacts"], list)
    
    # The search matches first_name, last_name, email, and phone
    # Since all contacts have "jo" in their email (john@example.com), all will match
    # Let's update the test to check for specific names instead
    contact_names = [f"{c['first_name']} {c['last_name']}" for c in data["contacts"]]
    assert "John Doe" in contact_names
    assert "Bob Johnson" in contact_names
    
    # Now search for something more specific
    response = client.get(
        "/api/contacts?search=Jane",
        headers=headers
    )
    
    assert response.status_code == 200
    data = json.loads(response.data)
    assert len(data["contacts"]) == 1
    assert data["contacts"][0]["first_name"] == "Jane"


def test_get_contacts_group_filter(client, auth_headers, create_user, create_contact, create_group):
    """Test getting contacts with group filter."""
    # Create a user and get auth headers
    user = create_user()
    headers = auth_headers(client)
    
    # Create some contacts
    contact1 = create_contact(user.id, first_name="John", last_name="Doe")
    contact2 = create_contact(user.id, first_name="Jane", last_name="Smith")
    contact3 = create_contact(user.id, first_name="Bob", last_name="Johnson")
    
    # Create a group
    group = create_group(user.id, name="Family")
    
    # Add contacts to group using the API instead of directly
    response = client.post(
        f"/api/contacts/{contact1.id}/groups",
        json={"group_id": group.id},
        headers=headers
    )
    assert response.status_code == 200
    
    response = client.post(
        f"/api/contacts/{contact2.id}/groups",
        json={"group_id": group.id},
        headers=headers
    )
    assert response.status_code == 200
    
    # Filter contacts by group
    response = client.get(
        f"/api/contacts?group=Family",
        headers=headers
    )
    
    assert response.status_code == 200
    data = json.loads(response.data)
    assert "contacts" in data
    assert isinstance(data["contacts"], list)
    assert len(data["contacts"]) == 2
    
    # Check that the right contacts are in the group
    contact_names = [f"{c['first_name']} {c['last_name']}" for c in data["contacts"]]
    assert "John Doe" in contact_names
    assert "Jane Smith" in contact_names
    assert "Bob Johnson" not in contact_names


def test_get_contact(client, auth_headers, create_user, create_contact):
    """Test getting a specific contact."""
    # Create a user and get auth headers
    user = create_user()
    headers = auth_headers(client)
    
    # Create a contact
    contact = create_contact(user.id, first_name="John", last_name="Doe")
    
    # Get the contact
    response = client.get(
        f"/api/contacts/{contact.id}",
        headers=headers
    )
    
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data["id"] == contact.id
    assert data["first_name"] == "John"
    assert data["last_name"] == "Doe"


def test_get_contact_not_found(client, auth_headers):
    """Test getting a contact that doesn't exist."""
    headers = auth_headers(client)
    
    response = client.get(
        "/api/contacts/999",
        headers=headers
    )
    
    assert response.status_code == 404
    data = json.loads(response.data)
    assert "message" in data
    assert "Contact not found" in data["message"]


def test_create_contact(client, auth_headers):
    """Test creating a new contact."""
    headers = auth_headers(client)
    
    contact_data = {
        "first_name": "John",
        "last_name": "Doe",
        "email": "john@example.com",
        "phone": "123-456-7890",
        "address": "123 Test St",
        "notes": "Test notes"
    }
    
    response = client.post(
        "/api/contacts",
        data=json.dumps(contact_data),
        headers=headers,
        content_type="application/json"
    )
    
    assert response.status_code == 201
    data = json.loads(response.data)
    assert "id" in data
    assert "message" in data
    assert data["message"] == "Contact created"
    
    # Check that the contact was created in the database
    contact_id = data["id"]
    response = client.get(
        f"/api/contacts/{contact_id}",
        headers=headers
    )
    
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data["first_name"] == "John"
    assert data["last_name"] == "Doe"
    assert data["email"] == "john@example.com"
    assert data["phone"] == "123-456-7890"
    assert data["address"] == "123 Test St"
    assert data["notes"] == "Test notes"


def test_create_contact_missing_first_name(client, auth_headers):
    """Test creating a contact without a first name."""
    headers = auth_headers(client)
    
    contact_data = {
        "last_name": "Doe",
        "email": "john@example.com"
    }
    
    response = client.post(
        "/api/contacts",
        data=json.dumps(contact_data),
        headers=headers,
        content_type="application/json"
    )
    
    assert response.status_code == 400
    data = json.loads(response.data)
    assert "message" in data
    assert "First name is required" in data["message"]


def test_update_contact(client, auth_headers, create_user, create_contact):
    """Test updating a contact."""
    # Create a user and get auth headers
    user = create_user()
    headers = auth_headers(client)
    
    # Create a contact
    contact = create_contact(user.id, first_name="John", last_name="Doe")
    
    # Update the contact
    update_data = {
        "first_name": "Johnny",
        "last_name": "Smith",
        "email": "johnny@example.com"
    }
    
    response = client.put(
        f"/api/contacts/{contact.id}",
        data=json.dumps(update_data),
        headers=headers,
        content_type="application/json"
    )
    
    assert response.status_code == 200
    data = json.loads(response.data)
    assert "message" in data
    assert data["message"] == "Contact updated"
    
    # Check that the contact was updated in the database
    response = client.get(
        f"/api/contacts/{contact.id}",
        headers=headers
    )
    
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data["first_name"] == "Johnny"
    assert data["last_name"] == "Smith"
    assert data["email"] == "johnny@example.com"


def test_update_contact_not_found(client, auth_headers):
    """Test updating a contact that doesn't exist."""
    headers = auth_headers(client)
    
    update_data = {
        "first_name": "Johnny",
        "last_name": "Smith"
    }
    
    response = client.put(
        "/api/contacts/999",
        data=json.dumps(update_data),
        headers=headers,
        content_type="application/json"
    )
    
    assert response.status_code == 404
    data = json.loads(response.data)
    assert "message" in data
    assert "Contact not found" in data["message"]


def test_delete_contact(client, auth_headers, create_user, create_contact):
    """Test deleting a contact."""
    # Create a user and get auth headers
    user = create_user()
    headers = auth_headers(client)
    
    # Create a contact
    contact = create_contact(user.id, first_name="John", last_name="Doe")
    
    # Delete the contact
    response = client.delete(
        f"/api/contacts/{contact.id}",
        headers=headers
    )
    
    assert response.status_code == 200
    data = json.loads(response.data)
    assert "message" in data
    assert data["message"] == "Contact deleted"
    
    # Check that the contact was deleted from the database
    response = client.get(
        f"/api/contacts/{contact.id}",
        headers=headers
    )
    
    assert response.status_code == 404


def test_delete_contact_not_found(client, auth_headers):
    """Test deleting a contact that doesn't exist."""
    headers = auth_headers(client)
    
    response = client.delete(
        "/api/contacts/999",
        headers=headers
    )
    
    assert response.status_code == 404
    data = json.loads(response.data)
    assert "message" in data
    assert "Contact not found" in data["message"]


def test_add_contact_to_group(client, auth_headers, create_user, create_contact, create_group):
    """Test adding a contact to a group."""
    # Create a user and get auth headers
    user = create_user()
    headers = auth_headers(client)
    
    # Create a contact and a group
    contact = create_contact(user.id, first_name="John", last_name="Doe")
    group = create_group(user.id, name="Family")
    
    # Add the contact to the group
    response = client.post(
        f"/api/contacts/{contact.id}/groups",
        data=json.dumps({
            "group_id": group.id
        }),
        headers=headers,
        content_type="application/json"
    )
    
    assert response.status_code == 200
    data = json.loads(response.data)
    assert "message" in data
    assert data["message"] == "Contact added to group"
    
    # Check that the contact is in the group
    response = client.get(
        f"/api/contacts/{contact.id}",
        headers=headers
    )
    
    assert response.status_code == 200
    data = json.loads(response.data)
    assert len(data["groups"]) == 1
    assert data["groups"][0]["id"] == group.id
    assert data["groups"][0]["name"] == "Family" 