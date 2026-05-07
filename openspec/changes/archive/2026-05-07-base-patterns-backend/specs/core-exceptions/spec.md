## ADDED Requirements

### Requirement: Core exceptions map to standard HTTP status codes
The system SHALL provide a hierarchy of custom exceptions that automatically map to standard HTTP status codes via middleware.

#### Scenario: NotFoundException maps to 404
- **WHEN** a service raises `NotFoundException`
- **THEN** the middleware converts it to an HTTP 404 response

#### Scenario: ConflictException maps to 409
- **WHEN** a service raises `ConflictException`
- **THEN** the middleware converts it to an HTTP 409 response

#### Scenario: UnauthorizedException maps to 401
- **WHEN** a service raises `UnauthorizedException`
- **THEN** the middleware converts it to an HTTP 401 response

#### Scenario: ForbiddenException maps to 403
- **WHEN** a service raises `ForbiddenException`
- **THEN** the middleware converts it to an HTTP 403 response

#### Scenario: ValidationException maps to 422
- **WHEN** a service raises `ValidationException`
- **THEN** the middleware converts it to an HTTP 422 response

### Requirement: AppException base class carries status_code and detail
All core exceptions SHALL extend a common `AppException` base class that carries a `status_code` (int) and `detail` (str).

#### Scenario: Exception carries structured error detail
- **WHEN** an `AppException` is raised with `detail="Resource not found"`
- **THEN** the HTTP response body contains `{"detail": "Resource not found"}`
