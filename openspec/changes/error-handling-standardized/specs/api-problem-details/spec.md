## ADDED Requirements

### Requirement: Error responses follow RFC 7807 Problem Details format

The system SHALL return all HTTP 4xx and 5xx error responses in RFC 7807 Problem Details format (`application/problem+json`).

#### Scenario: AppException returns RFC 7807 body
- **WHEN** a service raises `AppException` with status_code=404, detail="Recurso no encontrado", code="RESOURCE_NOT_FOUND"
- **THEN** the response body SHALL contain `type`, `title`, `status`, `detail`, `instance`, `requestId`, and `timestamp` fields

#### Scenario: Validation errors include errors array
- **WHEN** a request fails Pydantic validation with multiple field errors
- **THEN** the response SHALL include an `errors` array with each entry containing `field`, `message`, and `code`

#### Scenario: Unhandled exception returns RFC 7807 with status 500
- **WHEN** an unexpected exception occurs
- **THEN** the response SHALL use RFC 7807 format with status=500, title="Internal Server Error", detail="Internal server error"

#### Scenario: Media type is application/problem+json
- **WHEN** the API returns an error response
- **THEN** the Content-Type header SHALL be `application/problem+json`

### Requirement: RFC 7807 body includes requestId for traceability

The system SHALL include the request's unique identifier in the error response body as `requestId`.

#### Scenario: Error response includes X-Request-ID value
- **WHEN** an error occurs during request processing
- **THEN** the error body SHALL contain a `requestId` field matching the `X-Request-ID` response header

### Requirement: RFC 7807 body includes timestamp

The system SHALL include an ISO 8601 UTC timestamp in every error response.

#### Scenario: Error response includes timestamp
- **WHEN** an error response is generated
- **THEN** the body SHALL contain a `timestamp` field in ISO 8601 UTC format (e.g., `2026-05-14T12:00:00Z`)

### Requirement: Error code field for programmatic identification

The system SHALL provide a stable `code` string in error responses for programmatic error identification.

#### Scenario: AppException includes code in response
- **WHEN** a `NotFoundException` with code="RESOURCE_NOT_FOUND" is raised
- **THEN** the response SHALL include `"code": "RESOURCE_NOT_FOUND"`

#### Scenario: Non-AppException errors omit code
- **WHEN** an unhandled 500 error occurs
- **THEN** the `code` field SHALL be omitted or null
