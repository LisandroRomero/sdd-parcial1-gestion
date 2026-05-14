## MODIFIED Requirements

### Requirement: Middleware catches unhandled exceptions and returns structured JSON

The system SHALL provide a middleware that catches all unhandled exceptions and returns a structured RFC 7807 Problem Details JSON error response.

**Reason:** Migrate from `{"detail": ...}` to RFC 7807 (`application/problem+json`) as the single canonical format across all 4xx/5xx responses.

#### Scenario: Unhandled exception returns 500 with RFC 7807 body
- **WHEN** a request triggers an unhandled exception
- **THEN** the middleware returns an HTTP 500 response with `type`, `title`, `status`, `detail`, `instance`, `requestId`, and `timestamp` fields following RFC 7807

#### Scenario: AppException returns RFC 7807 with mapped status code and code field
- **WHEN** a service raises an `AppException` (e.g., `NotFoundException`)
- **THEN** the middleware returns the corresponding HTTP status code, the `detail` from the exception, and the `code` field with the exception's identifier (e.g., `"RESOURCE_NOT_FOUND"`)

#### Scenario: ValidationError from Pydantic returns 422 with errors array
- **WHEN** a request body fails Pydantic validation
- **THEN** the middleware returns HTTP 422 with RFC 7807 body including an `errors` array with `field`, `message`, and `code` for each validation failure

#### Scenario: RequestValidationError from FastAPI returns 422 with errors array
- **WHEN** a request fails FastAPI path/query validation
- **THEN** the middleware returns HTTP 422 with RFC 7807 body including an `errors` array with `field`, `message`, and `code` for each validation failure

### Requirement: Middleware adds X-Request-ID header and propagates to error body

The system SHALL provide middleware that assigns a unique request ID to each incoming request, exposes it via the `X-Request-ID` response header, and propagates it to `request.state.request_id` for inclusion in error bodies.

**Reason:** Request ID was in headers only; now also needed in the RFC 7807 body as `requestId`.

#### Scenario: Request receives unique ID in header and state
- **WHEN** a client sends a request without `X-Request-ID` header
- **THEN** the system generates a UUID, includes it in the response as `X-Request-ID`, and stores it in `request.state.request_id`

#### Scenario: Client-provided request ID is preserved
- **WHEN** a client sends a request with an `X-Request-ID` header
- **THEN** the system uses that value as the request ID, echoes it back in the response header, and stores it in `request.state.request_id`

### Requirement: Middleware sanitizes inputs

The system SHALL provide configurable middleware that sanitizes incoming request data to prevent XSS and SQL injection attempts.

#### Scenario: XSS attempt in string field returns 400
- **WHEN** a request contains HTML tags in a string field (e.g., `<script>alert('xss')</script>`)
- **THEN** the middleware strips HTML tags OR returns HTTP 400 with RFC 7807 body and code="INPUT_SANITIZATION"

#### Scenario: SQLi attempt in query param returns 400
- **WHEN** a query parameter contains SQL injection patterns (e.g., `' OR '1'='1`)
- **THEN** the middleware returns HTTP 400 with RFC 7807 body and code="INPUT_SANITIZATION"

#### Scenario: Sanitization middleware is configurable
- **WHEN** `SANITIZE_INPUTS` setting is `false`
- **THEN** the sanitization middleware SHALL NOT be applied
