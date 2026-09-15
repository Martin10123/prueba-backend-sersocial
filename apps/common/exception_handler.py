from rest_framework.views import exception_handler as drf_exception_handler

from apps.common.exceptions import DomainError
from apps.common.logging import get_logger

logger = get_logger(__name__)


def custom_exception_handler(exc, context):
    if isinstance(exc, DomainError):
        logger.warning(
            "domain_error",
            code=exc.code,
            message=exc.message,
            view=getattr(context.get("view"), "__class__", type(None)).__name__,
        )
        from rest_framework.response import Response

        return Response(
            {"detail": exc.message, "code": exc.code},
            status=exc.status_code,
        )

    response = drf_exception_handler(exc, context)
    if response is not None:
        return response

    logger.exception("unhandled_error", error=str(exc))
    from rest_framework.response import Response
    from rest_framework import status

    return Response(
        {"detail": "Error interno del servidor.", "code": "internal_error"},
        status=status.HTTP_500_INTERNAL_SERVER_ERROR,
    )
