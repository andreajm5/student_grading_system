# Architecture Documentation

This document describes the system architecture, design patterns, and technical decisions for the Student Grading System.

## System Overview

The Student Grading System is a RESTful API built with FastAPI, designed to handle homework submission and grading workflows for educational institutions.

## Technology Stack

- **Framework**: FastAPI 0.104+
- **Database**: MySQL 5.7+ / 8.x
- **ORM**: SQLModel (combines SQLAlchemy + Pydantic)
- **Containerization**: Docker + Docker Compose (recommended)
- **Authentication**: JWT (JSON Web Tokens)
- **Password Hashing**: bcrypt via passlib
- **Migrations**: Alembic
- **ASGI Server**: Uvicorn

## Architecture Layers

### 1. API Layer (`app/api/`)

FastAPI routers that handle HTTP requests and responses.

**Responsibilities:**
- Request validation (via Pydantic models)
- Response serialization
- HTTP status code management
- Dependency injection for authentication and database sessions

**Example Structure:**
```
app/api/
├── __init__.py
├── deps.py          # Shared dependencies (auth, db session)
├── auth.py          # Authentication endpoints
├── users.py         # User management endpoints
├── classrooms.py    # Classroom endpoints
├── lessons.py       # Lesson endpoints
├── assignments.py  # Assignment endpoints
├── submissions.py  # Submission endpoints
└── grading.py      # Grading endpoints
```

### 2. Service Layer (`app/services/`)

Business logic layer that processes domain operations.

**Responsibilities:**
- Business rule enforcement
- Data transformation
- Cross-cutting concerns (permissions, validation)
- Transaction management coordination

**Example Structure:**
```
app/services/
├── __init__.py
├── auth_service.py
├── classroom_service.py
├── assignment_service.py
├── submission_service.py
└── grading_service.py
```

### 3. Model Layer (`app/models/`)

SQLModel table models representing database entities.

**Responsibilities:**
- Database schema definition
- Relationship mapping
- Data validation (via Pydantic)

**Example Structure:**
```
app/models/
├── __init__.py
├── user.py
├── classroom.py
├── lesson.py
├── assignment.py
└── submission.py
```

### 4. Schema Layer (`app/schemas/`)

Pydantic models for request/response validation (if separated from SQLModel).

**Responsibilities:**
- API contract definition
- Input validation
- Output serialization
- Documentation generation

**Note**: SQLModel models can serve dual purpose (database + API), but separate schemas provide more flexibility.

### 5. Database Layer (`app/db/`)

Database connection and session management.

**Responsibilities:**
- Database engine initialization
- Session factory
- Connection pooling
- Migration management

**Example Structure:**
```
app/db/
├── __init__.py
├── session.py       # SQLModel engine and session
└── base.py         # Base model class
```

## Data Flow

```
HTTP Request
    ↓
FastAPI Router (app/api/)
    ↓
Dependency Injection (auth, db session)
    ↓
Service Layer (app/services/)
    ↓
Model Layer (app/models/) + Database Session
    ↓
MySQL Database
    ↓
Response Serialization
    ↓
HTTP Response
```

## Domain Model Relationships

```
User (STUDENT/TEACHER)
    ↓
    ├──→ Classroom (owned by TEACHER)
    │       ↓
    │       ├──→ Lesson (belongs to Classroom)
    │       │       ↓
    │       │       └──→ Assignment (belongs to Lesson)
    │       │               ↓
    │       │               └──→ Submission (belongs to Assignment, created by STUDENT)
    │       │                       ↓
    │       │                       └──→ Grade (embedded in Submission, created by TEACHER)
    │       │
    │       └──→ Enrollment (many-to-many: Classroom ↔ STUDENT)
    │
    └──→ Submission (created by STUDENT)
```

## Authentication & Authorization

### Authentication Flow

1. User submits credentials via `/auth/login`
2. System validates credentials against database
3. JWT token generated with user ID and role
4. Token returned to client
5. Client includes token in `Authorization: Bearer <token>` header
6. Protected endpoints validate token via dependency injection

### Authorization Rules

- **Students**:
  - Can only view/modify their own submissions
  - Can view classrooms/lessons they are enrolled in
  - Cannot create/modify assignments or grades

- **Teachers**:
  - Can manage classrooms they own
  - Can create lessons within their classrooms
  - Can create assignments for their lessons
  - Can grade any submission for assignments in their classrooms
  - Cannot modify other teachers' classrooms

### Implementation

```python
# app/api/deps.py
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

async def get_current_user(token: str = Depends(oauth2_scheme)):
    # Validate token and return user
    ...

async def require_teacher(current_user: User = Depends(get_current_user)):
    if current_user.role != "TEACHER":
        raise HTTPException(status_code=403, detail="Teacher access required")
    return current_user
```

## Database Design Principles

### 1. Normalization

- Follow 3NF to reduce data redundancy
- Use foreign keys for referential integrity
- Index frequently queried fields (user_id, classroom_id, assignment_id)

### 2. Soft Deletes (Optional)

Consider adding `deleted_at` timestamp for important entities to enable recovery:
- Users
- Classrooms
- Assignments

### 3. Audit Fields

Include timestamps on all entities:
- `created_at`: Record creation time
- `updated_at`: Last modification time

### 4. Relationships

- **One-to-Many**: Classroom → Lessons, Lesson → Assignments, Assignment → Submissions
- **Many-to-Many**: Classroom ↔ Students (via enrollment table)
- **Foreign Keys**: Always define with appropriate CASCADE rules

## File Upload Strategy

### Storage Options

1. **Local Filesystem** (Development/Simple Deployment)
   - Store in `uploads/` directory
   - Store file path in database
   - Simple but not scalable

2. **Cloud Storage** (Production)
   - AWS S3, Azure Blob, or Alibaba OSS
   - Store object key/URL in database
   - Scalable and reliable

### Implementation Considerations

- Validate file type and size before upload
- Generate unique filenames to prevent conflicts
- Store original filename in database for display
- Implement cleanup job for orphaned files

## Error Handling Strategy

### HTTP Status Codes

- `200 OK`: Successful GET/PUT/PATCH
- `201 Created`: Successful POST
- `400 Bad Request`: Invalid input
- `401 Unauthorized`: Missing/invalid token
- `403 Forbidden`: Insufficient permissions
- `404 Not Found`: Resource doesn't exist
- `422 Unprocessable Entity`: Validation errors
- `500 Internal Server Error`: Server errors

### Error Response Format

```json
{
  "detail": "Human-readable error message"
}
```

For validation errors:
```json
{
  "detail": [
    {
      "loc": ["body", "field_name"],
      "msg": "error message",
      "type": "value_error"
    }
  ]
}
```

## Performance Considerations

### Database Optimization

- Use indexes on foreign keys and frequently filtered columns
- Implement pagination for list endpoints
- Use `select_related` / `joinedload` to avoid N+1 queries
- Consider database connection pooling

### Caching Strategy (Future)

- Cache frequently accessed data (user info, classroom lists)
- Use Redis for session storage (if scaling horizontally)
- Cache assignment lists per lesson

### Async Operations

- Use async/await for I/O-bound operations
- Database queries should be async-compatible (SQLModel with async driver)

## Security Considerations

### Input Validation

- Validate all user inputs via Pydantic models
- Sanitize file uploads (check MIME types, scan for malware)
- Prevent SQL injection (use ORM, never raw SQL with user input)

### Password Security

- Hash passwords with bcrypt (cost factor 12+)
- Never store plaintext passwords
- Implement password strength requirements

### Token Security

- Use short-lived access tokens (60 minutes default)
- Implement refresh token mechanism (optional)
- Store tokens securely on client side
- Invalidate tokens on logout

### File Upload Security

- Limit file size (e.g., 10MB max)
- Whitelist allowed file types
- Scan uploaded files for malware
- Store files outside web root when possible

## Testing Strategy

### Unit Tests

- Test service layer logic in isolation
- Mock database dependencies
- Test edge cases and error conditions

### Integration Tests

- Test API endpoints with test database
- Test authentication and authorization flows
- Test database relationships and constraints

### Test Structure

```
tests/
├── __init__.py
├── conftest.py          # Pytest fixtures
├── test_auth.py
├── test_classrooms.py
├── test_assignments.py
└── test_submissions.py
```

## Deployment Architecture

### Single Server Deployment

```
Internet
    ↓
Nginx (Reverse Proxy + SSL)
    ↓
Uvicorn (FastAPI App)
    ↓
MySQL Database
```

### Docker Compose Deployment (Recommended)

```
Internet
    ↓
Nginx (optional)
    ↓
Docker Compose
    ├── API container (Uvicorn + FastAPI)
    └── MySQL container
```

### Scalable Deployment (Future)

```
Load Balancer
    ↓
Multiple Uvicorn Workers/Servers
    ↓
Shared MySQL Database
    ↓
Cloud Storage (S3/OSS) for Files
```

## Future Enhancements

- **Microservices**: Split into separate services (auth, assignments, grading)
- **Message Queue**: Use RabbitMQ/Redis for async tasks (email notifications, file processing)
- **Search**: Integrate Elasticsearch for full-text search
- **Real-time**: WebSocket support for live notifications
- **Analytics**: Separate analytics service for reporting
