## MODIFIED Requirements

### Requirement: System can create access tokens

The system SHALL provide a function to create signed JWT access tokens with a configurable expiration. The function SHALL accept an optional `data` dict to include additional claims (e.g., `role`) in the token payload.

#### Scenario: Create access token with user data

- **WHEN** `create_access_token(subject="user-id", data={"role": "CLIENT"})` is called
- **THEN** a signed JWT string is returned containing the subject, role, expiration claims, and any extra data from the `data` parameter

#### Scenario: Access token expires after configured TTL

- **WHEN** an access token is created with default TTL
- **THEN** the token's `exp` claim reflects ACCESS_TOKEN_EXPIRE_MINUTES from settings

#### Scenario: Create access token without extra data

- **WHEN** `create_access_token(subject="user-id")` is called with no `data` argument
- **THEN** a signed JWT string is returned containing only the standard claims (sub, iat, exp, type)
