from __future__ import annotations


class AppException(Exception):
    """Base exception for all application-level errors.

    Carries an HTTP status code and a human-readable detail message.
    Middleware catches these and converts them to JSON error responses.
    """

    def __init__(self, status_code: int, detail: str, code: str | None = None) -> None:
        self.status_code = status_code
        self.detail = detail
        self.code = code
        super().__init__(detail)


class NotFoundException(AppException):
    def __init__(self, detail: str = "Recurso no encontrado", code: str | None = "RESOURCE_NOT_FOUND") -> None:
        super().__init__(status_code=404, detail=detail, code=code)


class ConflictException(AppException):
    def __init__(self, detail: str = "Conflicto con el estado actual del recurso", code: str | None = "CONFLICT") -> None:
        super().__init__(status_code=409, detail=detail, code=code)


class UnauthorizedException(AppException):
    def __init__(self, detail: str = "No autenticado", code: str | None = "UNAUTHORIZED") -> None:
        super().__init__(status_code=401, detail=detail, code=code)


class ForbiddenException(AppException):
    def __init__(self, detail: str = "No autorizado para esta acción", code: str | None = "FORBIDDEN") -> None:
        super().__init__(status_code=403, detail=detail, code=code)


class ValidationException(AppException):
    def __init__(self, detail: str = "Error de validación", code: str | None = "VALIDATION_ERROR") -> None:
        super().__init__(status_code=422, detail=detail, code=code)


class BadRequestException(AppException):
    def __init__(self, detail: str = "Solicitud inválida", code: str | None = "BAD_REQUEST") -> None:
        super().__init__(status_code=400, detail=detail, code=code)
