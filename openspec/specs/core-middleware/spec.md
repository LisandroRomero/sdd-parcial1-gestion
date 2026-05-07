## ADDED Requirements

### Requirement: Middleware catches unhandled exceptions and returns structured JSON
The system SHALL provide a middleware that catches all unhandled exceptions and returns a structured JSON error response.

#### Scenario: Unhandled exception returns 500 with detail
- **WHEN** a request triggers an unhandled exception
- **THEN** the middleware returns an HTTP 500 response with `{"detail": "Internal server error"}`

#### Scenario: AppException returns mapped status code
- **WHEN** a service raises an `AppException` (e.g., `NotFoundException`)
- **THEN** the middleware returns the corresponding HTTP status code and detail from the exception

### Requirement: Middleware adds X-Request-ID header
The system SHALL provide middleware that assigns a unique request ID to each incoming request and exposes it via the `X-Request-ID` response header.

#### Scenario: Request receives unique ID
- **WHEN** a client sends a request without `X-Request-ID` header
- **THEN** the system generates a UUID and includes it in the response as `X-Request-ID`

#### Scenario: Client-provided request ID is preserved
- **WHEN** a client sends a request with an `X-Request-ID` header
- **THEN** the system uses that value as the request ID and echoes it back in the response
