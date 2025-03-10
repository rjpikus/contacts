# Getting Started Guide

This guide will help you set up and run the Contact Management Application on your local machine.

## Prerequisites

Before you begin, ensure you have the following installed:

- [Docker](https://www.docker.com/get-started) and [Docker Compose](https://docs.docker.com/compose/install/)
- [Node.js](https://nodejs.org/) (version 20 or later) - for local frontend development
- [Python](https://www.python.org/downloads/) (version 3.11 or later) - for local backend development
- [Git](https://git-scm.com/downloads) - for cloning the repository

## Running with Docker (Recommended)

The easiest way to get started is using Docker, which will set up the entire application stack for you.

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/contacts-app.git
   cd contacts-app
   ```

2. Start the application using Docker Compose:
   ```bash
   docker-compose up
   ```

3. Access the application:
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:5000

4. To stop the application, press `Ctrl+C` in the terminal or run:
   ```bash
   docker-compose down
   ```

## Local Development Setup

If you want to develop the application locally without Docker, follow these steps:

### Backend Setup

1. Navigate to the backend directory:
   ```bash
   cd backend
   ```

2. Create and activate a virtual environment:
   ```bash
   # On macOS/Linux
   python -m venv venv
   source venv/bin/activate

   # On Windows
   python -m venv venv
   venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Set up environment variables:
   ```bash
   # On macOS/Linux
   export FLASK_APP=app.py
   export FLASK_ENV=development
   export DATABASE_URL=postgresql://user:password@localhost:5432/contacts_db

   # On Windows
   set FLASK_APP=app.py
   set FLASK_ENV=development
   set DATABASE_URL=postgresql://user:password@localhost:5432/contacts_db
   ```

5. Initialize the database:
   ```bash
   flask db init
   flask db migrate -m "Initial migration"
   flask db upgrade
   ```

6. Run the Flask development server:
   ```bash
   flask run
   ```

### Frontend Setup

1. Navigate to the frontend directory:
   ```bash
   cd frontend
   ```

2. Install dependencies:
   ```bash
   yarn install
   # or
   npm install
   ```

3. Run the Next.js development server:
   ```bash
   yarn dev
   # or
   npm run dev
   ```

4. Access the frontend at http://localhost:3000

## Database Setup

If you're running the backend locally, you'll need a PostgreSQL database:

1. Install PostgreSQL:
   - [PostgreSQL Downloads](https://www.postgresql.org/download/)

2. Create a database:
   ```sql
   CREATE DATABASE contacts_db;
   CREATE USER user WITH PASSWORD 'password';
   GRANT ALL PRIVILEGES ON DATABASE contacts_db TO user;
   ```

3. Update the `DATABASE_URL` environment variable to match your database configuration.

## Testing the API

You can test the API using tools like [Postman](https://www.postman.com/) or [curl](https://curl.se/).

Example API request to register a user:

```bash
curl -X POST http://localhost:5000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email": "user@example.com", "password": "securepassword"}'
```

For more API documentation, see [API Documentation](./api-documentation.md).

## Troubleshooting

### Common Issues

1. **Database connection errors**:
   - Ensure PostgreSQL is running
   - Check that the database credentials are correct
   - Verify the database exists

2. **Port conflicts**:
   - If ports 3000 or 5000 are already in use, you can change them in the `docker-compose.yml` file

3. **Docker issues**:
   - Try rebuilding the containers: `docker-compose build --no-cache`
   - Check Docker logs: `docker-compose logs`

### Getting Help

If you encounter any issues not covered here, please:
1. Check the project's issue tracker
2. Search for similar issues in the project's documentation
3. Create a new issue with detailed information about your problem 