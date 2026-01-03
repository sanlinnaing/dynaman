# Auth Service Implementation

## Architecture
The authentication service is designed as a standalone microservice (`auth-service`) using FastAPI. It handles user registration, authentication (login), and user management.

### Key Components:
- **API Gateway (Nginx):** Routes requests to `/auth/` to the auth service. Acts as a pass-through proxy.
- **Auth Service:**
    - **Database:** Uses MongoDB (via Motor) to store user data.
    - **Security:** Uses `bcrypt` for password hashing and `python-jose` for JWT generation/validation.
    - **Role-Based Access Control (RBAC):** Supports `SYSTEM_ADMIN`, `USER_ADMIN`, and `USER` roles.
    - **CORS:** Uses `CORSMiddleware` to handle Cross-Origin Resource Sharing.

## Fixes & Updates
- **CORS Handling:** Nginx gateway configuration simplified to pass requests through. `CORSMiddleware` added to `auth-service` (and existing in `engine`) to handle CORS headers and `OPTIONS` requests directly. This resolves conflicting headers and 405 errors.
- **Dependencies:** Updated `requirements.txt` to use `pydantic[email]` to resolve `ImportError: email-validator is not installed`.
- **Password Safety:** `SecurityService` updated to truncate passwords to 72 bytes (UTF-8 encoded) to prevent `ValueError` from `bcrypt`.

## User Roles
- **SYSTEM_ADMIN:** Can manage all resources, including creating other admins and modifying schemas.
- **USER_ADMIN:** Can manage users but cannot create System Admins.
- **USER:** Standard user, can access data based on permissions (default read/write for configured schemas, restricted from admin tasks).

## Initial Setup
- **Default Admin:** `admin@dynaman.com` / `admin` (seeded on startup).
