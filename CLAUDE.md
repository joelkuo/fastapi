# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a FastAPI REST API application with JWT authentication, PostgreSQL database using SQLModel ORM, and Alembic for migrations. The application supports CRUD operations for posts, user management, authentication, and voting functionality.

## Development Commands

### Running the Application

**Local development:**
```bash
uvicorn app.main:app --reload
```

**Docker development:**
```bash
docker-compose up
# Rebuilds and starts: API service on port 8000, PostgreSQL database
```

### Database Migrations

**Create migration:**
```bash
alembic revision --autogenerate -m "description"
```

**Apply migrations:**
```bash
alembic upgrade head
```

**Rollback migration:**
```bash
alembic downgrade -1
```

### Testing

**Run all tests:**
```bash
pytest
```

**Run specific test file:**
```bash
pytest test/test_posts.py
```

**Run with verbose output:**
```bash
pytest -v -s
```

## Architecture

### Application Structure

- `app/main.py` - FastAPI application entry point with router registration and CORS middleware
- `app/database.py` - Database models (SQLModel) and Pydantic schemas, engine configuration, session management with connection pooling
- `app/config.py` - Environment configuration using pydantic-settings (reads from .env file)
- `app/oauth2.py` - JWT authentication logic, token creation/verification, user dependency injection
- `app/utils.py` - Password hashing utilities using bcrypt
- `app/routers/` - API route handlers organized by domain (post, user, auth, vote)

### Database Architecture

**Connection Management:**
- Uses `lifespan` context manager in `app/database.py` for application-level connection pooling (1-5 connections)
- `SessionDep` dependency provides per-request database sessions
- Connection pooling enables concurrent request handling across multiple database connections

**ORM Pattern:**
- SQLModel classes (e.g., `post`, `User`, `Vote`) define database tables with relationships
- Pydantic models (e.g., `UserCreate`, `UserOutput`, `PostCreate`) handle API request/response validation
- Foreign key constraints with CASCADE deletion (posts deleted when user is deleted)

**Key relationships:**
- `User` has many `posts` (one-to-many via `owner_id`)
- `User` can vote on `posts` (many-to-many through `Vote` table)

### Authentication Flow

1. User credentials validated via `/login` endpoint (OAuth2 password flow)
2. JWT access token created with `user_id` payload and expiration
3. Protected routes use `UserDep` dependency which:
   - Extracts token from Authorization header
   - Verifies JWT signature and expiration
   - Loads user from database
   - Injects authenticated user into endpoint

### Router Pattern

Routes are organized by domain in `app/routers/`:
- `post.py` - Post CRUD with voting aggregation using SQLAlchemy joins
- `user.py` - User registration
- `auth.py` - Login/token generation
- `vote.py` - Voting on posts

All routers use FastAPI's `APIRouter` with prefixes and tags for automatic OpenAPI documentation.

## Configuration

### Environment Variables

Required variables (configured in `.env` or docker-compose environment):
- `DATABASE_HOSTNAME` - PostgreSQL host
- `DATABASE_PASSWORD` - PostgreSQL password
- `DATABASE_USERNAME` - PostgreSQL username
- `DATABASE_NAME` - Database name
- `DATABASE_PORT` - PostgreSQL port (typically 5432)
- `SECRET_KEY` - JWT signing key
- `ALGORITHM` - JWT algorithm (typically HS256)
- `ACCESS_TOKEN_EXPIRE_MINUTES` - Token expiration time

### Docker Setup

The `docker-compose.yml` defines two services:
- `api` - FastAPI application with hot-reload
- `postgres` - PostgreSQL database with persistent volume

## Testing

Tests use pytest with fixtures in `test/conftest.py`:
- `test_engine` - Creates temporary test database
- `test_db` - Provides test database session
- `client` - TestClient with dependency overrides
- `test_user`, `test_user2` - Pre-created test users
- `authorized_client` - TestClient with authentication headers
- `test_posts` - Pre-created test posts

Test database naming: production database name + `_test` suffix (e.g., `fastapi_test`)
