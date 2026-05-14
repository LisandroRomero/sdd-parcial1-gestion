## MODIFIED Requirements

### Requirement: Core exceptions map to standard HTTP status codes with stable codes

The system SHALL provide a hierarchy of custom exceptions that automatically map to standard HTTP status codes via middleware, each carrying a stable `code` identifier for programmatic error handling.

**Reason:** Added `code` field to `AppException` for stable programmatic error identification in both backend and frontend.

#### Scenario: NotFoundException maps to 404 with code RESOURCE_NOT_FOUND
- **WHEN** a service raises `NotFoundException`
- **THEN** the middleware converts it to an HTTP 404 response with `code: "RESOURCE_NOT_FOUND"`

#### Scenario: ConflictException maps to 409 with code CONFLICT
- **WHEN** a service raises `ConflictException`
- **THEN** the middleware converts it to an HTTP 409 response with `code: "CONFLICT"`

#### Scenario: UnauthorizedException maps to 401 with code UNAUTHORIZED
- **WHEN** a service raises `UnauthorizedException`
- **THEN** the middleware converts it to an HTTP 401 response with `code: "UNAUTHORIZED"`

#### Scenario: ForbiddenException maps to 403 with code FORBIDDEN
- **WHEN** a service raises `ForbiddenException`
- **THEN** the middleware converts it to an HTTP 403 response with `code: "FORBIDDEN"`

#### Scenario: ValidationException maps to 422 with code VALIDATION_ERROR
- **WHEN** a service raises `ValidationException`
- **THEN** the middleware converts it to an HTTP 422 response with `code: "VALIDATION_ERROR"`

#### Scenario: BadRequestException maps to 400 with code BAD_REQUEST
- **WHEN** a service raises `BadRequestException`
- **THEN** the middleware converts it to an HTTP 400 response with `code: "BAD_REQUEST"`

### Requirement: AppException base class carries status_code, detail, and code

All core exceptions SHALL extend a common `AppException` base class that carries a `status_code` (int), `detail` (str), and optional `code` (str).

**Reason:** Added `code` field for stable programmatic error identification.

#### Scenario: Exception carries structured error detail with code
- **WHEN** an `AppException` is raised with `detail="Resource not found"` and `code="RESOURCE_NOT_FOUND"`
- **THEN** the HTTP response body SHALL contain `detail`, `code`, and all other RFC 7807 required fields

#### Scenario: Exception without explicit code defaults to None
- **WHEN** an `AppException` is raised without specifying `code`
- **THEN** the exception's `code` attribute SHALL be `None` and omitted from the response body
