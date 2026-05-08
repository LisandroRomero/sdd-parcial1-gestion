from __future__ import annotations


class AppException(Exception):
    """Base exception for all application-level errors.

    Carries an HTTP status code and a human-readable detail message.
    Middleware catches these and converts them to JSON error responses.
    """

    def __init__(self, status_code: int, detail: str) -> None:
        self.status_code = status_code
        self.detail = detail
        super().__init__(detail)


class NotFoundException(AppException):
    def __init__(self, detail: str = "Recurso no encontrado") -> None:
        super().__init__(status_code=404, detail=detail)


class ConflictException(AppException):
    def __init__(self, detail: str = "Conflicto con el estado actual del recurso") -> None:
        super().__init__(status_code=409, detail=detail)


class UnauthorizedException(AppException):
    def __init__(self, detail: str = "No autenticado") -> None:
        super().__init__(status_code=401, detail=detail)


class ForbiddenException(AppException):
    def __init__(self, detail: str = "No autorizado para esta acción") -> None:
        super().__init__(status_code=403, detail=detail)


class ValidationException(AppException):
    def __init__(self, detail: str = "Error de validación") -> None:
        super().__init__(status_code=422, detail=detail)


class BadRequestException(AppException):
    def __init__(self, detail: str = "Solicitud inválida") -> None:
        super().__init__(status_code=400, detail=detail)
