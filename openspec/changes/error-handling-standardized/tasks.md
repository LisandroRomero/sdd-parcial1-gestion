## 1. Contract And Docs Alignment

- [ ] 1.1 Update `docs/Integrador.txt` API error section to match RFC 7807 canonical contract (include example with extensions: `code`, `errors`, `requestId`, `timestamp`)
- [ ] 1.2 Update `backend/README.md` to replace `{ statusCode, message }` error example with RFC 7807 Problem Details example

## 2. Backend RFC 7807 Implementation

- [ ] 2.1 Add `code` optional field to `AppException.__init__()` and set default codes in all subclasses (`RESOURCE_NOT_FOUND`, `CONFLICT`, `UNAUTHORIZED`, `FORBIDDEN`, `VALIDATION_ERROR`, `BAD_REQUEST`)
- [ ] 2.2 Create single `global_exception_handler` in `middleware.py` that produces RFC 7807 `application/problem+json` for all exception types (`AppException`, `RequestValidationError`, `ValidationError`, `Exception`), replacing the 4 separate handlers
- [ ] 2.3 Remove duplicated `ValidationError` handler from `RequestIDMiddleware.dispatch` — delegate all error handling to the unified global handler
- [ ] 2.4 Ensure `X-Request-ID` is always present in headers and propagated via `request.state.request_id` into the RFC 7807 `requestId` field in the body
- [ ] 2.5 Add `timestamp` (ISO 8601 UTC) and `instance` (request URL path) to every RFC 7807 response body

## 3. Input Sanitization Middleware

- [ ] 3.1 Create `InputSanitizationMiddleware` in `middleware.py` that strips HTML tags from string fields (XSS prevention)
- [ ] 3.2 Add SQLi pattern detection for query params and string fields, rejecting with 400 and code `INPUT_SANITIZATION`
- [ ] 3.3 Make sanitization configurable via `settings.SANITIZE_INPUTS` (off by default)
- [ ] 3.4 Register `InputSanitizationMiddleware` conditionally in `main.py` based on settings

## 4. Frontend RFC 7807 Alignment

- [ ] 4.1 Update `getErrorMessage` to parse RFC 7807: prefer `errors[0].message` (validations), fallback to `detail`, fallback to HTTP code map
- [ ] 4.2 Add missing HTTP codes to frontend error map: `409 → "Conflicto con el estado actual del recurso."`, `422 → "Error de validación. Revisá los datos ingresados."`, `401 → "Sesión expirada. Iniciá sesión de nuevo."`
- [ ] 4.3 Expose `requestId` from RFC 7807 responses in the helper for logging/debug purposes (without showing to end user)

## 5. Verification

- [ ] 5.1 Manually inspect representative endpoints in OpenAPI docs to confirm error schema examples are consistent with RFC 7807
- [ ] 5.2 Verify changes don't break existing consumers by grepping for `statusCode`/`message` assumptions and updating call sites
- [ ] 5.3 Test XSS sanitization by sending `<script>` tags through string fields
- [ ] 5.4 Test SQLi sanitization by sending SQL injection patterns through query params
