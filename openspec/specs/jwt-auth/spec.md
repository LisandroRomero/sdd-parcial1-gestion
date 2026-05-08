## Requirements

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

### Requirement: System can verify access tokens
The system SHALL provide a function to decode and verify JWT access tokens, returning the payload or raising an appropriate exception.

#### Scenario: Verify valid token returns payload
- **WHEN** `verify_token(token)` is called with a valid, non-expired token
- **THEN** the decoded payload is returned

#### Scenario: Verify expired token raises UnauthorizedException
- **WHEN** `verify_token(token)` is called with an expired token
- **THEN** an `UnauthorizedException` is raised

#### Scenario: Verify invalid signature raises UnauthorizedException
- **WHEN** `verify_token(token)` is called with a token signed with a different secret
- **THEN** an `UnauthorizedException` is raised

### Requirement: System can create refresh tokens
The system SHALL provide a function to create signed JWT refresh tokens with a longer expiration for token rotation.

#### Scenario: Create refresh token with longer TTL
- **WHEN** `create_refresh_token(subject="user-id")` is called
- **THEN** a signed JWT string is returned with an expiration longer than access tokens (configurable via settings)

### Requirement: System can hash and verify passwords
The system SHALL provide functions to hash passwords using bcrypt and verify plaintext against hashed values.

#### Scenario: Hash password produces verifiable hash
- **WHEN** `hash_password("secure-pass123")` is called
- **THEN** a bcrypt hash string is returned

#### Scenario: Verify correct password returns True
- **WHEN** `verify_password("secure-pass123", hash)` is called with the matching plaintext
- **THEN** `True` is returned

#### Scenario: Verify incorrect password returns False
- **WHEN** `verify_password("wrong-pass", hash)` is called with non-matching plaintext
- **THEN** `False` is returned
