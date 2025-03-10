# Contact Management Application - Test Suite

This directory contains the test suite for the Contact Management Application. The tests are organized into unit tests and integration tests to ensure comprehensive coverage of the application's functionality.

## Test Structure

- **Unit Tests**: Located in the `unit/` directory, these tests focus on individual components of the application, such as models.
  - `test_user_model.py`: Tests for the User model
  - `test_contact_model.py`: Tests for the Contact model
  - `test_group_model.py`: Tests for the Group model

- **Integration Tests**: Located in the `integration/` directory, these tests focus on the API endpoints and how components interact.
  - `test_auth_routes.py`: Tests for authentication endpoints
  - `test_contacts_routes.py`: Tests for contact management endpoints
  - `test_groups_routes.py`: Tests for group management endpoints

## Test Configuration

- `config.py`: Contains the TestConfig class that sets up an in-memory SQLite database for testing
- `conftest.py`: Contains fixtures for creating a Flask app, test client, and helper functions for creating users, contacts, and groups

## Running Tests

To run all tests:

```bash
python -m pytest
```

To run tests with coverage:

```bash
python -m pytest --cov=app
```

To generate a detailed HTML coverage report:

```bash
python -m pytest --cov=app --cov-report=html
```

To run specific test files:

```bash
python -m pytest tests/unit/test_user_model.py
python -m pytest tests/integration/test_auth_routes.py
```

## Test Coverage

The current test coverage is approximately 73%, with 100% coverage for the models. The main areas that need additional test coverage are:

1. `app/__init__.py`: 30% coverage - This file contains the application factory and initialization code
2. `app/routes/contacts.py`: 62% coverage - This file contains the contact management endpoints, with some complex import/export functionality that needs more tests

## Future Improvements

1. Add more tests for the import/export functionality in the contacts routes
2. Add tests for edge cases and error handling
3. Add performance tests for database operations
4. Add end-to-end tests with a real database 