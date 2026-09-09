# SmartPark AI — Security Evidence

## 1. Security Overview

SmartPark AI implements application-level security across authentication, authorization, password storage, protected API routes and request validation.

The supporting source-code evidence is retained in:

`security-source-evidence.txt`

---

## 2. Password Security

Password handling is implemented in:

`app/utils/security.py`

The backend uses:

`PasswordHash.recommended()`

from the `pwdlib` library.

Application functions include:

- `hash_password`
- `verify_password`

Passwords are therefore stored as password hashes rather than plaintext values.

---

## 3. JWT Authentication

The security utility provides functions for:

- creating access tokens;
- encoding JWT tokens;
- decoding JWT tokens.

Relevant implementation includes:

- `create_access_token`
- `jwt.encode`
- `jwt.decode`

JWT access tokens are used to authenticate protected API requests.

---

## 4. Authenticated User Protection

The backend uses:

`get_current_user`

as a FastAPI dependency.

Protected routes depend on the authenticated user before allowing access.

The captured source evidence confirms authenticated-user protection across modules including:

- parking sessions;
- predictions;
- reviews;
- payments;
- recommendations;
- vehicles;
- notifications;
- authentication profile access.

Unauthorized requests can return HTTP 401 responses.

---

## 5. Role-Based Administrator Authorization

Administrator functionality uses:

`require_admin`

The dependency verifies that:

`current_user.role == "admin"`

Requests from users without administrator privileges can return:

`HTTP 403 Forbidden`

The captured implementation shows administrator protection across:

- user management;
- analytics;
- review moderation;
- payments;
- notifications;
- reservations;
- parking management.

This provides backend authorization in addition to frontend route protection.

---

## 6. User Resource Isolation

Several protected routes pass the authenticated user's identifier into backend service operations.

Examples include:

- vehicle retrieval;
- prediction history;
- payment history;
- notification retrieval;
- parking-session history.

This design helps prevent users from retrieving another user's account-specific data through normal protected endpoints.

---

## 7. Input Validation

SmartPark AI uses Pydantic schemas for request and response validation.

Validation mechanisms include schema field definitions and typed request models.

Examples include:

- email validation;
- numeric constraints;
- string-length constraints;
- UUID validation;
- reservation input validation;
- parking-management input validation.

This reduces malformed or invalid data entering application services.

---

## 8. SQL and Database Safety

SQLAlchemy is used as the database access layer.

The application relies on ORM/query construction rather than manually concatenating user-controlled values into raw SQL commands.

Foreign-key constraints and application-level checks provide additional data-integrity protection.

---

## 9. Reservation Security and Validation

Reservation operations include validation for:

- authenticated ownership;
- parking availability;
- parking opening hours;
- reservation timing;
- check-in timing;
- active reservation state;
- checkout processing.

These checks protect the reservation lifecycle from invalid state transitions.

---

## 10. Payment and Refund Validation

Payment and refund operations are implemented through backend business logic rather than trusting frontend values alone.

Administrator refund functionality is restricted using `require_admin`.

Supported refunds are processed against recorded payment and wallet data.

---

## 11. Environment Configuration

Sensitive configuration is stored outside normal source files using environment variables.

Examples of values that must remain private include:

- database credentials;
- JWT secret;
- authentication tokens.

The project `.gitignore` excludes private environment configuration.

No secret values should be included in dissertation screenshots or evidence documents.

---

## 12. Test Database Isolation

Automated backend tests use a dedicated test database configuration.

The test setup includes safeguards against accidentally executing destructive automated tests against the normal development database.

This improves development safety and repeatability.

---

## 13. Security Scope

SmartPark AI implements appropriate prototype-level security mechanisms for authentication and application authorization.

However, the project should not be described as having undergone:

- professional penetration testing;
- external security certification;
- production infrastructure hardening;
- formal vulnerability assessment;
- PCI-DSS certification.

These would be appropriate areas for future production deployment work.

---

## 14. Evidence Files

Security evidence retained for the dissertation:

- `security-source-evidence.txt`
- `SECURITY_EVIDENCE.md`

The source evidence was generated directly from the implemented backend source code.

