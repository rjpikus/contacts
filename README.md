# Contact Management Application

A modern, web-based contact management system designed to allow users to create, edit, delete, search, and organize their contacts efficiently. It mimics the core functionality of iCloud Contacts or Google Contacts, with a clean user interface, robust backend, and secure data storage.

## Features

- User authentication (signup, login, logout)
- CRUD operations for contacts (Create, Read, Update, Delete)
- Contact search and filtering
- Contact grouping (e.g., tags or categories like "Family," "Work")
- Import/export contacts in CSV format
- Responsive UI with a modern design
- RESTful API for communication between frontend and backend
- Containerized deployment with Docker

## Tech Stack

- **Backend**: Python 3.11, Flask (RESTful API), Flask-SQLAlchemy (ORM), Flask-JWT-Extended (authentication)
- **Frontend**: Next.js 14 (React framework), TypeScript, Tailwind CSS (styling)
- **Database**: PostgreSQL 16
- **Containerization**: Docker, Docker Compose

## Project Structure

```
.
├── backend/                  # Flask backend
│   ├── app/                  # Application code
│   │   ├── models/           # Database models
│   │   ├── routes/           # API routes
│   │   └── utils/            # Utility functions
│   ├── migrations/           # Database migrations
│   ├── app.py                # Application entry point
│   ├── config.py             # Configuration
│   ├── Dockerfile            # Backend Docker configuration
│   └── requirements.txt      # Python dependencies
├── frontend/                 # Next.js frontend
│   ├── app/                  # Next.js app directory
│   │   ├── auth/             # Authentication pages
│   │   ├── contacts/         # Contact management pages
│   │   ├── groups/           # Group management pages
│   │   ├── globals.css       # Global styles
│   │   ├── layout.tsx        # Root layout
│   │   └── page.tsx          # Home page
│   ├── components/           # Reusable components
│   ├── lib/                  # Utilities and state management
│   ├── public/               # Static assets
│   ├── Dockerfile            # Frontend Docker configuration
│   └── package.json          # Node.js dependencies
├── docs/                     # Documentation
├── docker-compose.yml        # Docker Compose configuration
└── README.md                 # Project documentation
```

## Getting Started

### Prerequisites

- Docker and Docker Compose
- Node.js 20+ (for local frontend development)
- Python 3.11+ (for local backend development)

### Running with Docker

1. Clone the repository
2. Navigate to the project directory
3. Run the application with Docker Compose:

```bash
docker-compose up
```

The application will be available at:
- Frontend: http://localhost:3000
- Backend API: http://localhost:5000

### Local Development

#### Backend

1. Navigate to the backend directory
2. Create a virtual environment and activate it:

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:

```bash
pip install -r requirements.txt
```

4. Run the Flask development server:

```bash
flask run
```

#### Frontend

1. Navigate to the frontend directory
2. Install dependencies:

```bash
yarn install
```

3. Run the Next.js development server:

```bash
yarn dev
```

## API Documentation

### Authentication

- **POST /api/auth/register** - Register a new user
- **POST /api/auth/login** - Login and get access token
- **GET /api/auth/me** - Get current user information

### Contacts

- **GET /api/contacts** - Get all contacts (with optional search and group filters)
- **POST /api/contacts** - Create a new contact
- **GET /api/contacts/:id** - Get a specific contact
- **PUT /api/contacts/:id** - Update a contact
- **DELETE /api/contacts/:id** - Delete a contact
- **POST /api/contacts/import** - Import contacts from CSV
- **GET /api/contacts/export** - Export contacts to CSV

### Groups

- **GET /api/groups** - Get all groups
- **POST /api/groups** - Create a new group
- **GET /api/groups/:id** - Get a specific group
- **PUT /api/groups/:id** - Update a group
- **DELETE /api/groups/:id** - Delete a group
- **POST /api/contacts/:id/groups** - Add a contact to a group

## License

This project is licensed under the MIT License - see the LICENSE file for details.
