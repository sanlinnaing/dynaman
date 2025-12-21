# Dyna Management Tool - Backend Engine

## Introduction
The Dyna Management Tool Engine is a FastAPI-based backend designed to provide a flexible No-Code platform. It manages dynamic data entities through a metadata-driven architecture, separating schema definitions from data execution.

## Architecture
The project follows a Domain-Driven Design (DDD) inspired Clean Architecture:
- **api/**: Entry points (Routers, Dependencies).
- **building_blocks/**: Shared utilities, configuration, and types.
- **metadata_context/**: Handles Schema definitions (The "Builder" aspect).
- **execution_context/**: Handles Record data management (The "Runtime" aspect).

## Technologies Used
- **Language**: Python 3.13+
- **Framework**: FastAPI
- **Database Driver**: Motor (Async MongoDB)
- **Validation**: Pydantic v2
- **Testing**: Pytest, Pytest-Cov

## Getting Started

### Installation
1. Navigate to the `engine` directory.
2. Create a virtual environment:
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Configure environment variables in `.env` (copy example if available).

### Running the Application
```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

### Running Tests
The project maintains high test coverage (~93%). Use the configured `pytest` runner:
```bash
# Run all tests
pytest

# Run with coverage report
pytest --cov=. --cov-report=term-missing
```

## API Endpoints
- **/schemas** (`metadata_context`): Manage entity definitions (Create, Update, Delete Schemas and Fields).
- **/data** (`execution_context`): CRUD operations for records based on defined schemas.

## Development Notes
- **Database**: Uses MongoDB. For testing, a separate `dynaman_test` database is used and automatically cleaned up between tests.
- **Linting/Formatting**: Adhere to PEP 8.