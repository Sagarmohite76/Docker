# Docker Task API

A robust, production-ready RESTful Task and User Management API built with **FastAPI**, **SQLAlchemy**, and **PostgreSQL**, containerized using **Docker** and **Docker Compose**.

---

## 🚀 Features

- **User Management**: Complete CRUD operations for users with email uniqueness enforcement and secure PBKDF2-SHA256 password hashing.
- **Task Management**: Full task life cycle management with configurable statuses (`pending`, `in_progress`, `completed`, `cancelled`), priority levels (`low`, `medium`, `high`), and optional due dates.
- **Interactive Documentation**: Auto-generated Swagger UI (`/docs`) and ReDoc (`/redoc`) API documentation.
- **Data Validation & Settings**: Strict payload schema validation powered by Pydantic v2 and environment settings powered by `pydantic-settings`.
- **Containerization**: Fully containerized environment configured with Dockerfile and Docker Compose.
- **Health Monitoring**: Dedicated `/health` endpoint for monitoring API status and container orchestration probes.

---

## 🛠️ Tech Stack

- **Framework**: [FastAPI](https://fastapi.tiangolo.com/)
- **ORM**: [SQLAlchemy](https://www.sqlalchemy.org/)
- **Database**: [PostgreSQL](https://www.postgresql.org/) (Supports local PostgreSQL and managed cloud instances like Neon)
- **Data Validation & Settings**: [Pydantic v2](https://docs.pydantic.dev/) & [pydantic-settings](https://docs.pydantic.dev/latest/concepts/pydantic_settings/)
- **Security**: PBKDF2 with SHA-256 password hashing (`hashlib`)
- **Server**: [Uvicorn](https://www.uvicorn.org/)
- **Testing**: [Pytest](https://docs.pytest.org/) & [HTTPX](https://www.python-httpx.org/)
- **Containerization**: [Docker](https://www.docker.com/) & Docker Compose

---

## 📁 Project Structure

```text
docker-task-api/
├── app/
│   ├── api/
│   │   └── routes/
│   │       ├── tasks.py          # Task API endpoints
│   │       └── users.py          # User API endpoints
│   ├── core/
│   │   ├── config.py             # Application settings & environment variables
│   │   └── security.py           # Password hashing & verification utilities
│   ├── db/
│   │   ├── database.py           # SQLAlchemy engine & session setup
│   │   └── models.py             # Database ORM models (User, Task)
│   ├── schemas/
│   │   ├── task.py               # Pydantic schemas for tasks
│   │   └── user.py               # Pydantic schemas for users
│   ├── services/
│   │   ├── task_service.py       # Task business logic & DB operations
│   │   └── user_service.py       # User business logic & DB operations
│   └── main.py                   # FastAPI app entry point & route registration
├── .dockerignore                 # Docker ignore file
├── .env.example                  # Environment variable configuration template
├── docker-compose.yml            # Docker Compose orchestration file
├── Dockerfile                    # Docker build specifications
├── requirements.txt              # Project dependencies
└── README.md                     # Project documentation
```

---

## ⚙️ Environment Variables

Create a `.env` file in the project root based on `.env.example`:

```env
DATABASE_URL=postgresql://<username>:<password>@<host>:<port>/<dbname>?sslmode=require
```

---

## 📦 Getting Started

### Prerequisites

- Python 3.12+ (for local development)
- Docker & Docker Compose (for containerized setup)
- A running PostgreSQL database (or cloud database connection URL)

---

### Option A: Running with Docker Compose (Recommended)

1. **Clone the repository and navigate to the project directory:**
   ```bash
   git clone <repository-url>
   cd docker-task-api
   ```

2. **Configure Environment Variables:**
   Create `.env` file from the example template:
   ```bash
   cp .env.example .env
   ```
   Update `DATABASE_URL` in `.env` with your PostgreSQL database credentials.

3. **Build and Run the Containers:**
   ```bash
   docker compose up --build
   ```

4. **Access the API:**
   - **Base API**: [http://localhost:8000](http://localhost:8000)
   - **Health Check**: [http://localhost:8000/health](http://localhost:8000/health)
   - **Swagger Documentation**: [http://localhost:8000/docs](http://localhost:8000/docs)
   - **ReDoc Documentation**: [http://localhost:8000/redoc](http://localhost:8000/redoc)

---

### Option B: Running Locally with Python Virtual Environment

1. **Create and Activate a Virtual Environment:**
   ```bash
   # Windows (PowerShell)
   python -m venv venv
   .\venv\Scripts\activate

   # Linux / macOS
   python3 -m venv venv
   source venv/bin/activate
   ```

2. **Install Dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure Environment Variables:**
   Create a `.env` file containing your `DATABASE_URL`.

4. **Start the FastAPI Development Server:**
   ```bash
   uvicorn app.main:app --reload --port 8000
   ```

---

## 🔗 API Endpoints

### 🩺 Health Check

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/health` | Verify API connectivity and status |

---

### 👤 User Endpoints (`/users`)

| Method | Endpoint | Description | Status Code |
|---|---|---|---|
| `POST` | `/users/` | Create a new user account | `201 Created` |
| `GET` | `/users/` | Get list of all users (Paginated: `skip`, `limit`) | `200 OK` |
| `GET` | `/users/{user_id}` | Retrieve single user by ID | `200 OK` |
| `PATCH` | `/users/{user_id}` | Update existing user details | `200 OK` |
| `DELETE` | `/users/{user_id}` | Delete user account | `204 No Content` |

---

### 📋 Task Endpoints (`/tasks`)

| Method | Endpoint | Description | Status Code |
|---|---|---|---|
| `POST` | `/tasks/` | Create a new task | `201 Created` |
| `GET` | `/tasks/` | Get all tasks for the user | `200 OK` |
| `GET` | `/tasks/{task_id}` | Retrieve a specific task by ID | `200 OK` |
| `PATCH` | `/tasks/{task_id}` | Update task details | `200 OK` |
| `DELETE` | `/tasks/{task_id}` | Delete a task | `204 No Content` |

---

## 📊 Data Models

### User Schema
* `id` (int, primary key)
* `name` (string, required)
* `email` (string, unique, required)
* `password` (string, write-only on creation/update)
* `created_at` (datetime)
* `updated_at` (datetime)

### Task Schema
- `id` (int, primary key)
- `user_id` (int, foreign key -> users.id)
- `title` (string, required)
- `description` (string, optional)
- `status` (`pending` | `in_progress` | `completed` | `cancelled`)
- `priority` (`low` | `medium` | `high`)
- `due_date` (datetime, optional)
- `created_at` (datetime)
- `updated_at` (datetime)

