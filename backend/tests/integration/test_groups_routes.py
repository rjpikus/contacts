import pytest
import json
from app.models.group import Group


def test_get_groups_empty(client, auth_headers):
    """Test getting all groups when there are none."""
    headers = auth_headers(client)
    
    response = client.get(
        "/api/groups",
        headers=headers
    )
    
    assert response.status_code == 200
    data = json.loads(response.data)
    assert "groups" in data
    assert isinstance(data["groups"], list)
    assert len(data["groups"]) == 0


def test_get_groups(client, auth_headers, create_user, create_group):
    """Test getting all groups."""
    # Create a user and get auth headers
    user = create_user()
    headers = auth_headers(client)
    
    # Create some groups
    create_group(user.id, name="Family")
    create_group(user.id, name="Work")
    
    # Get groups
    response = client.get(
        "/api/groups",
        headers=headers
    )
    
    assert response.status_code == 200
    data = json.loads(response.data)
    assert "groups" in data
    assert isinstance(data["groups"], list)
    assert len(data["groups"]) == 2
    
    # Check the groups data
    assert any(g["name"] == "Family" for g in data["groups"])
    assert any(g["name"] == "Work" for g in data["groups"])


def test_get_group(client, auth_headers, create_user, create_group):
    """Test getting a specific group."""
    # Create a user and get auth headers
    user = create_user()
    headers = auth_headers(client)
    
    # Create a group
    group = create_group(user.id, name="Family")
    
    # Get the group
    response = client.get(
        f"/api/groups/{group.id}",
        headers=headers
    )
    
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data["id"] == group.id
    assert data["name"] == "Family"
    assert data["user_id"] == user.id
    assert "contacts_count" in data
    assert data["contacts_count"] == 0


def test_get_group_not_found(client, auth_headers):
    """Test getting a group that doesn't exist."""
    headers = auth_headers(client)
    
    response = client.get(
        "/api/groups/999",
        headers=headers
    )
    
    assert response.status_code == 404
    data = json.loads(response.data)
    assert "message" in data
    assert "Group not found" in data["message"]


def test_create_group(client, auth_headers):
    """Test creating a new group."""
    headers = auth_headers(client)
    
    group_data = {
        "name": "Family"
    }
    
    response = client.post(
        "/api/groups",
        data=json.dumps(group_data),
        headers=headers,
        content_type="application/json"
    )
    
    assert response.status_code == 201
    data = json.loads(response.data)
    assert "id" in data
    assert "message" in data
    assert data["message"] == "Group created"
    
    # Check that the group was created in the database
    group_id = data["id"]
    response = client.get(
        f"/api/groups/{group_id}",
        headers=headers
    )
    
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data["name"] == "Family"


def test_create_group_missing_name(client, auth_headers):
    """Test creating a group without a name."""
    headers = auth_headers(client)
    
    group_data = {}
    
    response = client.post(
        "/api/groups",
        data=json.dumps(group_data),
        headers=headers,
        content_type="application/json"
    )
    
    assert response.status_code == 400
    data = json.loads(response.data)
    assert "message" in data
    assert "Group name is required" in data["message"]


def test_create_group_duplicate_name(client, auth_headers, create_user, create_group):
    """Test creating a group with a name that already exists."""
    # Create a user and get auth headers
    user = create_user()
    headers = auth_headers(client)
    
    # Create a group
    create_group(user.id, name="Family")
    
    # Try to create another group with the same name
    group_data = {
        "name": "Family"
    }
    
    response = client.post(
        "/api/groups",
        data=json.dumps(group_data),
        headers=headers,
        content_type="application/json"
    )
    
    assert response.status_code == 400
    data = json.loads(response.data)
    assert "message" in data
    assert "A group with this name already exists" in data["message"]


def test_update_group(client, auth_headers, create_user, create_group):
    """Test updating a group."""
    # Create a user and get auth headers
    user = create_user()
    headers = auth_headers(client)
    
    # Create a group
    group = create_group(user.id, name="Family")
    
    # Update the group
    update_data = {
        "name": "Close Family"
    }
    
    response = client.put(
        f"/api/groups/{group.id}",
        data=json.dumps(update_data),
        headers=headers,
        content_type="application/json"
    )
    
    assert response.status_code == 200
    data = json.loads(response.data)
    assert "message" in data
    assert data["message"] == "Group updated"
    
    # Check that the group was updated in the database
    response = client.get(
        f"/api/groups/{group.id}",
        headers=headers
    )
    
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data["name"] == "Close Family"


def test_update_group_not_found(client, auth_headers):
    """Test updating a group that doesn't exist."""
    headers = auth_headers(client)
    
    update_data = {
        "name": "Close Family"
    }
    
    response = client.put(
        "/api/groups/999",
        data=json.dumps(update_data),
        headers=headers,
        content_type="application/json"
    )
    
    assert response.status_code == 404
    data = json.loads(response.data)
    assert "message" in data
    assert "Group not found" in data["message"]


def test_update_group_missing_name(client, auth_headers, create_user, create_group):
    """Test updating a group without providing a name."""
    # Create a user and get auth headers
    user = create_user()
    headers = auth_headers(client)
    
    # Create a group
    group = create_group(user.id, name="Family")
    
    # Update the group without a name
    update_data = {}
    
    response = client.put(
        f"/api/groups/{group.id}",
        data=json.dumps(update_data),
        headers=headers,
        content_type="application/json"
    )
    
    assert response.status_code == 400
    data = json.loads(response.data)
    assert "message" in data
    assert "Group name is required" in data["message"]


def test_update_group_duplicate_name(client, auth_headers, create_user, create_group):
    """Test updating a group with a name that already exists for another group."""
    # Create a user and get auth headers
    user = create_user()
    headers = auth_headers(client)
    
    # Create two groups
    group1 = create_group(user.id, name="Family")
    group2 = create_group(user.id, name="Work")
    
    # Try to update group2 to have the same name as group1
    update_data = {
        "name": "Family"
    }
    
    response = client.put(
        f"/api/groups/{group2.id}",
        data=json.dumps(update_data),
        headers=headers,
        content_type="application/json"
    )
    
    assert response.status_code == 400
    data = json.loads(response.data)
    assert "message" in data
    assert "A group with this name already exists" in data["message"]


def test_delete_group(client, auth_headers, create_user, create_group):
    """Test deleting a group."""
    # Create a user and get auth headers
    user = create_user()
    headers = auth_headers(client)
    
    # Create a group
    group = create_group(user.id, name="Family")
    
    # Delete the group
    response = client.delete(
        f"/api/groups/{group.id}",
        headers=headers
    )
    
    assert response.status_code == 200
    data = json.loads(response.data)
    assert "message" in data
    assert data["message"] == "Group deleted"
    
    # Check that the group was deleted from the database
    response = client.get(
        f"/api/groups/{group.id}",
        headers=headers
    )
    
    assert response.status_code == 404


def test_delete_group_not_found(client, auth_headers):
    """Test deleting a group that doesn't exist."""
    headers = auth_headers(client)
    
    response = client.delete(
        "/api/groups/999",
        headers=headers
    )
    
    assert response.status_code == 404
    data = json.loads(response.data)
    assert "message" in data
    assert "Group not found" in data["message"] 