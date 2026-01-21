
# Student Grading System v1.0.0

An online homework collection and grading platform built with **FastAPI**, **MySQL**, **SQLModel**, and **Docker**.

This project focuses on the core workflow:

- Students upload their homework submissions
- Teachers review, grade, and give feedback

The teaching structure is explicitly modeled as:

- One **classroom** has **multiple lessons**
- One **lesson** has **multiple assignments**
- One **assignment** has **multiple submissions** (typically one per student)

---

## Project Overview

The **Student Grading System** is designed for schools and training institutions that need a structured, web-based workflow for managing homework at scale.

- **Students**
  - View classrooms and lessons they are enrolled in
  - Browse published assignments per lesson
  - Upload homework submissions (file + optional text)
  - View grades and teacher feedback

- **Teachers**
  - Manage classrooms, lessons, and enrollment
  - Create and publish assignments under a specific lesson
  - Review submissions, score them, and leave feedback
  - Track submission states (on-time / late / missing)

---

## Core Features

- **Authentication & Authorization**
  - Roles: `STUDENT`, `TEACHER`
  - Token-based authentication (e.g. JWT)
  - Role-based access control on endpoints

- **Classroom & Lesson Management**
  - Create classrooms and lessons
  - Enroll students into classrooms (many-to-many)
  - Organize assignments by lesson within a classroom

- **Assignment Management**
  - Create assignments with title, description, due date, and max score
  - Publish/unpublish assignments
  - List/filter assignments by classroom, lesson, and time window

- **Submission Workflow**
  - Students submit homework per assignment
  - Support file uploads + optional text answer
  - Track timestamps to identify late submissions
  - Optional resubmission policy (teacher-controlled)

- **Grading & Feedback**
  - Teachers grade submissions with numeric score and feedback comment
  - Track `graded_at` and `graded_by`
  - Students can view their own grading results

- **Reporting (Extensible)**
  - Per-assignment stats: average/min/max score, submission rate
  - Per-student progress: completed vs missing assignments

---

## Backend Architecture

- **Framework**: [FastAPI](https://fastapi.tiangolo.com/)
- **Database**: [MySQL](https://www.mysql.com/)
- **ORM**: [SQLModel](https://sqlmodel.tiangolo.com/) (Pydantic + SQLAlchemy)

Recommended backend structure (conceptual):

- `app/main.py`: FastAPI app initialization
- `app/api/`: routers/endpoints (REST)
- `app/models/`: SQLModel table models
- `app/schemas/`: request/response models (if separated from SQLModel)
- `app/services/`: business logic (grading rules, permissions, workflows)
- `app/db/`: session, engine, migrations, initialization

Key design principles:

- **Separation of concerns**: router → service → persistence
- **Schema-first APIs**: request/response validation via Pydantic/SQLModel
- **Secure by default**: RBAC, password hashing, access checks

---

## Data Model (Conceptual)

Main entities (simplified):

- **User**
  - `id`
  - `email`, `full_name`, `hashed_password`
  - `role` (`STUDENT` or `TEACHER`)

- **Classroom**
  - `id`
  - `name`, `description`
  - `teacher_id` (owner / primary teacher)
  - Enrollment: many-to-many with student users

- **Lesson**
  - `id`
  - `classroom_id`
  - `title`, `description`
  - `scheduled_at`

- **Assignment**
  - `id`
  - `lesson_id`
  - `title`, `description`
  - `due_at`, `max_score`
  - `is_published`

- **Submission**
  - `id`
  - `assignment_id`, `student_id`
  - `submitted_at`
  - `content` (optional text)
  - `file_path` (or storage key)

- **Grading (stored in `Submission` or separate `Grade`)**
  - `score`
  - `feedback`
  - `graded_at`
  - `graded_by` (teacher id)

Relationship summary:

- `Classroom 1 -> N Lesson`
- `Lesson 1 -> N Assignment`
- `Assignment 1 -> N Submission`
- `User(STUDENT) 1 -> N Submission`

---

## API Design (Proposed)

The API is organized around RESTful resources. Example route groups:

- `/auth`
  - `POST /auth/register`
  - `POST /auth/login`

- `/users`
  - `GET /users/me`

- `/classrooms`
  - `POST /classrooms`
  - `GET /classrooms`
  - `GET /classrooms/{classroom_id}`
  - `POST /classrooms/{classroom_id}/enroll` (teacher enrolls a student)

- `/lessons`
  - `POST /lessons`
  - `GET /classrooms/{classroom_id}/lessons`

- `/assignments`
  - `POST /assignments`
  - `GET /lessons/{lesson_id}/assignments`
  - `GET /assignments/{assignment_id}`

- `/submissions`
  - `POST /assignments/{assignment_id}/submissions` (student submits)
  - `GET /assignments/{assignment_id}/submissions` (teacher views all)
  - `GET /submissions/{submission_id}`

- `/grading`
  - `POST /submissions/{submission_id}/grade`
  - `PATCH /submissions/{submission_id}/grade`

Notes:

- Students can only access their own submissions.
- Teachers can only manage classrooms/lessons/assignments they own and can grade related submissions.

---

## Installation & Setup

### Prerequisites

- Python 3.10+  
- MySQL server (5.7+ or 8.x)  
- `pip` (or Poetry)
- Docker + Docker Compose (recommended)

### Option A: Run with Docker (Recommended)

1. Create an environment file:

```bash
cp env.example .env
```

1. Start the stack (API + MySQL):

```bash
docker compose up --build
```

1. Open API docs:

- Swagger UI: `http://127.0.0.1:8000/docs`
- ReDoc: `http://127.0.0.1:8000/redoc`

> Note: If you don’t have `docker-compose.yml` yet, see `docs/DEPLOYMENT.md` for a recommended Compose setup.

### Option B: Run Locally (Without Docker)

### 1. Clone the Repository

```bash
git clone <your-repo-url> student_grading_system
cd student_grading_system
```

### 2. Create and Activate a Virtual Environment

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables

Create a `.env` file in the project root:

```env
DATABASE_URL=mysql+mysqlconnector://USER:PASSWORD@HOST:PORT/DB_NAME
SECRET_KEY=your-jwt-secret-key
ACCESS_TOKEN_EXPIRE_MINUTES=60
```

You can start from the provided template:

```bash
cp env.example .env
```

### 5. Database Initialization / Migrations

This project may use Alembic or SQLModel metadata creation. Run the appropriate init/migration command for your codebase.

### 6. Run the API

```bash
uvicorn app.main:app --reload
```

Docs:

- Swagger UI: `http://127.0.0.1:8000/docs`
- ReDoc: `http://127.0.0.1:8000/redoc`

---

## Development Guidelines

- Use type hints and docstrings for functions (services, utilities, routers).
- Keep business logic in services; routers should stay thin.
- Enforce RBAC: students only see/modify their own data; teachers only manage their own classrooms.
- Use secure password hashing (e.g. bcrypt) and short-lived access tokens (JWT).

---

## Roadmap

- Cloud file storage integration (S3/OSS) and signed upload URLs
- Rubric-based grading templates
- Notifications for new assignments and released grades
- Admin role for institution-wide management
- Frontend SPA (React/Vue) consuming this API

---

## Documentation

Comprehensive documentation is available in the [`docs/`](./docs/) directory:

- **[API Documentation](./docs/API.md)** - Complete API reference with endpoints and examples
- **[Architecture Guide](./docs/ARCHITECTURE.md)** - System design and technical decisions
- **[Deployment Guide](./docs/DEPLOYMENT.md)** - Production deployment instructions
- **[Contributing Guide](./docs/CONTRIBUTING.md)** - Development guidelines and contribution process

## License

MIT License - See [LICENSE](./LICENSE) file for details.
