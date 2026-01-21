# Contributing Guide

Thank you for your interest in contributing to the Student Grading System! This document provides guidelines and instructions for contributing.

## Development Setup

### Option A: Docker (Recommended)

1. **Create `.env`**

   ```bash
   cp env.example .env
   ```

2. **Run API + MySQL**

   ```bash
   docker compose up --build
   ```

3. **Open API Docs**

   - Swagger UI: `http://127.0.0.1:8000/docs`
   - ReDoc: `http://127.0.0.1:8000/redoc`

### Option B: Local Python (Without Docker)

1. **Fork and Clone**
   ```bash
   git clone https://github.com/your-username/student_grading_system.git
   cd student_grading_system
   ```

2. **Create Virtual Environment**
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # Windows: .venv\Scripts\activate
   ```

3. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   pip install -r requirements-dev.txt  # If available
   ```

4. **Set Up Environment Variables**
   ```bash
   cp env.example .env
   # Edit .env with your local database credentials
   ```

5. **Initialize Database**
   ```bash
   # Run migrations or initialization script
   alembic upgrade head
   # or
   python -m app.database.init_db
   ```

## Code Style

### Python Style Guide

- Follow [PEP 8](https://www.python.org/dev/peps/pep-0008/)
- Use type hints for all function parameters and return values
- Maximum line length: 100 characters
- Use 4 spaces for indentation (no tabs)

### Formatting Tools

We recommend using:
- `black` for code formatting
- `flake8` or `ruff` for linting
- `mypy` for type checking

```bash
# Format code
black app/ tests/

# Lint code
flake8 app/ tests/

# Type check
mypy app/
```

### Docstring Convention

Use Google-style docstrings:

```python
def create_assignment(
    lesson_id: int,
    title: str,
    max_score: float,
    db: Session = Depends(get_db)
) -> Assignment:
    """
    Create a new assignment for a lesson.

    Args:
        lesson_id: The ID of the lesson this assignment belongs to
        title: The title of the assignment
        max_score: Maximum possible score for this assignment
        db: Database session

    Returns:
        The created Assignment object

    Raises:
        HTTPException: If lesson not found or user lacks permission
    """
    ...
```

## Git Workflow

### Branch Naming

- `feature/` - New features (e.g., `feature/add-rubric-grading`)
- `bugfix/` - Bug fixes (e.g., `bugfix/fix-submission-deadline`)
- `docs/` - Documentation updates (e.g., `docs/update-api-docs`)
- `refactor/` - Code refactoring (e.g., `refactor/optimize-db-queries`)

### Commit Messages

Follow [Conventional Commits](https://www.conventionalcommits.org/):

```
<type>(<scope>): <subject>

<body>

<footer>
```

Types:
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting, etc.)
- `refactor`: Code refactoring
- `test`: Adding or updating tests
- `chore`: Maintenance tasks

Examples:
```
feat(assignments): add due date reminder notification

fix(submissions): correct file upload size validation

docs(api): update authentication endpoint documentation
```

### Pull Request Process

1. **Create a branch** from `main`:
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make your changes** and commit:
   ```bash
   git add .
   git commit -m "feat(scope): description"
   ```

3. **Push to your fork**:
   ```bash
   git push origin feature/your-feature-name
   ```

4. **Create Pull Request** on GitHub with:
   - Clear title and description
   - Reference related issues
   - List changes made
   - Screenshots (if UI changes)

5. **Address review feedback**:
   - Respond to comments
   - Make requested changes
   - Update PR description if needed

## Testing

### Writing Tests

- Write tests for all new features
- Aim for >80% code coverage
- Test both success and error cases
- Use descriptive test names

Example:
```python
def test_create_assignment_success(db_session, teacher_user, lesson):
    """Test successful assignment creation by teacher."""
    assignment_data = {
        "lesson_id": lesson.id,
        "title": "Test Assignment",
        "max_score": 100
    }
    assignment = create_assignment(assignment_data, teacher_user, db_session)
    assert assignment.title == "Test Assignment"
    assert assignment.max_score == 100

def test_create_assignment_unauthorized(db_session, student_user, lesson):
    """Test that students cannot create assignments."""
    with pytest.raises(HTTPException) as exc:
        create_assignment({...}, student_user, db_session)
    assert exc.value.status_code == 403
```

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app --cov-report=html

# Run specific test file
pytest tests/test_assignments.py

# Run with verbose output
pytest -v
```

## Code Review Guidelines

### For Contributors

- Keep PRs focused and small (one feature/fix per PR)
- Ensure all tests pass
- Update documentation if needed
- Respond to review comments promptly

### For Reviewers

- Be constructive and respectful
- Check code quality, tests, and documentation
- Test the changes locally if possible
- Approve when satisfied

## Project Structure

When adding new features, follow the existing structure:

```
app/
├── api/          # API endpoints
├── models/       # SQLModel database models
├── schemas/      # Pydantic request/response models
├── services/     # Business logic
├── db/           # Database configuration
└── core/         # Core utilities (config, security)
```

## Questions?

- Open an issue for bugs or feature requests
- Check existing issues and PRs before creating new ones
- Be respectful and professional in all communications

Thank you for contributing! 🎉
