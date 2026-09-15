class DomainError(Exception):
    """Base domain/business rule error."""

    code = "domain_error"
    status_code = 400

    def __init__(self, message: str, *, code: str | None = None):
        super().__init__(message)
        self.message = message
        if code:
            self.code = code


class NotFoundError(DomainError):
    code = "not_found"
    status_code = 404


class ValidationError(DomainError):
    code = "validation_error"
    status_code = 400


class PermissionDeniedError(DomainError):
    code = "permission_denied"
    status_code = 403


class InvalidTransitionError(DomainError):
    code = "invalid_transition"
    status_code = 400
