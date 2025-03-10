# API Documentation

This document provides detailed information about the API endpoints available in the Contact Management Application.

## Base URL

All API endpoints are relative to the base URL:

```
http://localhost:5000/api
```

## Authentication

The API uses JWT (JSON Web Token) for authentication. Most endpoints require a valid token to be included in the request headers.

### Headers

For protected endpoints, include the following header:

```
Authorization: Bearer <your_jwt_token>
```

### Endpoints

#### Register a new user

```
POST /auth/register
```

Request body:
```json
{
  "email": "user@example.com",
  "password": "securepassword"
}
```

Response:
```json
{
  "message": "User registered",
  "user_id": 1
}
```

#### Login

```
POST /auth/login
```

Request body:
```json
{
  "email": "user@example.com",
  "password": "securepassword"
}
```

Response:
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

#### Get current user

```
GET /auth/me
```

Response:
```json
{
  "id": 1,
  "email": "user@example.com",
  "created_at": "2023-01-01T12:00:00"
}
```

## Contacts

### Endpoints

#### Get all contacts

```
GET /contacts
```

Query parameters:
- `search`: Search term to filter contacts (optional)
- `group`: Group name to filter contacts (optional)

Response:
```json
{
  "contacts": [
    {
      "id": 1,
      "user_id": 1,
      "first_name": "John",
      "last_name": "Doe",
      "email": "john@example.com",
      "phone": "123-456-7890",
      "address": "123 Main St",
      "notes": "Some notes",
      "created_at": "2023-01-01T12:00:00",
      "updated_at": "2023-01-01T12:00:00",
      "groups": [
        {
          "id": 1,
          "name": "Family"
        }
      ]
    }
  ]
}
```

#### Get a specific contact

```
GET /contacts/:id
```

Response:
```json
{
  "id": 1,
  "user_id": 1,
  "first_name": "John",
  "last_name": "Doe",
  "email": "john@example.com",
  "phone": "123-456-7890",
  "address": "123 Main St",
  "notes": "Some notes",
  "created_at": "2023-01-01T12:00:00",
  "updated_at": "2023-01-01T12:00:00",
  "groups": [
    {
      "id": 1,
      "name": "Family"
    }
  ]
}
```

#### Create a new contact

```
POST /contacts
```

Request body:
```json
{
  "first_name": "Jane",
  "last_name": "Smith",
  "email": "jane@example.com",
  "phone": "987-654-3210",
  "address": "456 Oak St",
  "notes": "Work colleague",
  "group_ids": [2]
}
```

Response:
```json
{
  "id": 2,
  "message": "Contact created"
}
```

#### Update a contact

```
PUT /contacts/:id
```

Request body:
```json
{
  "first_name": "Jane",
  "last_name": "Smith-Johnson",
  "email": "jane.johnson@example.com",
  "group_ids": [2, 3]
}
```

Response:
```json
{
  "message": "Contact updated"
}
```

#### Delete a contact

```
DELETE /contacts/:id
```

Response:
```json
{
  "message": "Contact deleted"
}
```

#### Add a contact to a group

```
POST /contacts/:id/groups
```

Request body:
```json
{
  "group_id": 3
}
```

Response:
```json
{
  "message": "Contact added to group"
}
```

#### Import contacts from CSV

```
POST /contacts/import
```

Request:
- Content-Type: multipart/form-data
- Form field: `file` (CSV file)

CSV format:
```
first_name,last_name,email,phone,address,notes
John,Doe,john@example.com,123-456-7890,123 Main St,Some notes
Jane,Smith,jane@example.com,987-654-3210,456 Oak St,Work colleague
```

Response:
```json
{
  "message": "Imported 2 contacts"
}
```

#### Export contacts to CSV

```
GET /contacts/export
```

Response:
- Content-Type: text/csv
- File download: contacts.csv

## Groups

### Endpoints

#### Get all groups

```
GET /groups
```

Response:
```json
{
  "groups": [
    {
      "id": 1,
      "user_id": 1,
      "name": "Family",
      "contacts_count": 3
    },
    {
      "id": 2,
      "user_id": 1,
      "name": "Work",
      "contacts_count": 5
    }
  ]
}
```

#### Get a specific group

```
GET /groups/:id
```

Response:
```json
{
  "id": 1,
  "user_id": 1,
  "name": "Family",
  "contacts_count": 3
}
```

#### Create a new group

```
POST /groups
```

Request body:
```json
{
  "name": "Friends"
}
```

Response:
```json
{
  "id": 3,
  "message": "Group created"
}
```

#### Update a group

```
PUT /groups/:id
```

Request body:
```json
{
  "name": "Close Friends"
}
```

Response:
```json
{
  "message": "Group updated"
}
```

#### Delete a group

```
DELETE /groups/:id
```

Response:
```json
{
  "message": "Group deleted"
}
```

## Error Responses

The API returns appropriate HTTP status codes and error messages:

- 400 Bad Request: Invalid input data
- 401 Unauthorized: Missing or invalid authentication
- 404 Not Found: Resource not found
- 500 Internal Server Error: Server-side error

Example error response:
```json
{
  "message": "Email already registered"
}
``` 