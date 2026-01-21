# API Documentation

This document provides detailed information about the Student Grading System API endpoints.

## Base URL

```
http://localhost:8000/api/v1
```

> When running via Docker, the API is still exposed on port `8000` by default (see `docs/DEPLOYMENT.md`).

## Authentication

Most endpoints require authentication via JWT tokens. Include the token in the Authorization header:

```
Authorization: Bearer <your-token>
```

## Endpoints

### Authentication

#### Register User
```http
POST /auth/register
Content-Type: application/json

{
  "email": "user@example.com",
  "full_name": "John Doe",
  "password": "securepassword",
  "role": "STUDENT" | "TEACHER"
}
```

**Response:**
```json
{
  "id": 1,
  "email": "user@example.com",
  "full_name": "John Doe",
  "role": "STUDENT"
}
```

#### Login
```http
POST /auth/login
Content-Type: application/x-www-form-urlencoded

username=user@example.com&password=securepassword
```

**Response:**
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "token_type": "bearer"
}
```

### Users

#### Get Current User
```http
GET /users/me
Authorization: Bearer <token>
```

**Response:**
```json
{
  "id": 1,
  "email": "user@example.com",
  "full_name": "John Doe",
  "role": "STUDENT"
}
```

### Classrooms

#### Create Classroom (Teacher only)
```http
POST /classrooms
Authorization: Bearer <token>
Content-Type: application/json

{
  "name": "Class 3A",
  "description": "Advanced Mathematics"
}
```

#### List Classrooms
```http
GET /classrooms
Authorization: Bearer <token>
```

#### Get Classroom Details
```http
GET /classrooms/{classroom_id}
Authorization: Bearer <token>
```

#### Enroll Student (Teacher only)
```http
POST /classrooms/{classroom_id}/enroll
Authorization: Bearer <token>
Content-Type: application/json

{
  "student_id": 5
}
```

### Lessons

#### Create Lesson (Teacher only)
```http
POST /lessons
Authorization: Bearer <token>
Content-Type: application/json

{
  "classroom_id": 1,
  "title": "Introduction to Algebra",
  "description": "Basic algebraic concepts",
  "scheduled_at": "2024-01-15T10:00:00"
}
```

#### List Lessons in Classroom
```http
GET /classrooms/{classroom_id}/lessons
Authorization: Bearer <token>
```

### Assignments

#### Create Assignment (Teacher only)
```http
POST /assignments
Authorization: Bearer <token>
Content-Type: application/json

{
  "lesson_id": 1,
  "title": "Homework 1: Linear Equations",
  "description": "Solve the following problems...",
  "due_at": "2024-01-20T23:59:59",
  "max_score": 100,
  "is_published": true
}
```

#### List Assignments in Lesson
```http
GET /lessons/{lesson_id}/assignments
Authorization: Bearer <token>
```

#### Get Assignment Details
```http
GET /assignments/{assignment_id}
Authorization: Bearer <token>
```

### Submissions

#### Submit Homework (Student only)
```http
POST /assignments/{assignment_id}/submissions
Authorization: Bearer <token>
Content-Type: multipart/form-data

file: <file>
content: "Optional text answer"
```

**Response:**
```json
{
  "id": 1,
  "assignment_id": 1,
  "student_id": 2,
  "submitted_at": "2024-01-18T14:30:00",
  "content": "Optional text answer",
  "file_path": "/uploads/submission_1.pdf"
}
```

#### List Submissions for Assignment (Teacher only)
```http
GET /assignments/{assignment_id}/submissions
Authorization: Bearer <token>
```

#### Get Submission Details
```http
GET /submissions/{submission_id}
Authorization: Bearer <token>
```

### Grading

#### Grade Submission (Teacher only)
```http
POST /submissions/{submission_id}/grade
Authorization: Bearer <token>
Content-Type: application/json

{
  "score": 85,
  "feedback": "Good work! Minor errors in problem 3."
}
```

#### Update Grade (Teacher only)
```http
PATCH /submissions/{submission_id}/grade
Authorization: Bearer <token>
Content-Type: application/json

{
  "score": 90,
  "feedback": "Updated after review."
}
```

## Error Responses

All endpoints may return the following error responses:

### 400 Bad Request
```json
{
  "detail": "Validation error message"
}
```

### 401 Unauthorized
```json
{
  "detail": "Not authenticated"
}
```

### 403 Forbidden
```json
{
  "detail": "Not enough permissions"
}
```

### 404 Not Found
```json
{
  "detail": "Resource not found"
}
```

### 422 Unprocessable Entity
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

## Rate Limiting

Currently, no rate limiting is implemented. This may be added in future versions.

## Pagination

List endpoints support pagination via query parameters:

```
GET /classrooms?skip=0&limit=10
```

**Response:**
```json
{
  "items": [...],
  "total": 50,
  "skip": 0,
  "limit": 10
}
```
