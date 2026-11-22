import logging

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from src.application.errors.access_denied import AccessDeniedError
from src.application.errors.base import ApplicationError
from src.application.errors.invalid_signature import InvalidSignatureError
from src.domain.errors.account import AccountOwnershipMismatchError
from src.domain.errors.auth import InvalidCredentialsError
from src.domain.errors.base import DomainError, DomainValidationError
from src.domain.errors.common import AlreadyExistsError, NotFoundError
from src.presentation.errors.base import PresentationError
from src.presentation.errors.unauthorized import UnauthorizedError

logger = logging.getLogger(__name__)

_STATUS_BY_ERROR: dict[type[Exception], int] = {
    DomainValidationError: 400,
    InvalidCredentialsError: 401,
    InvalidSignatureError: 401,
    UnauthorizedError: 401,
    AccessDeniedError: 403,
    NotFoundError: 404,
    AlreadyExistsError: 409,
    AccountOwnershipMismatchError: 409,
}


async def _handle(request: Request, exc: Exception) -> JSONResponse:
    for error_type in type(exc).__mro__:
        status_code = _STATUS_BY_ERROR.get(error_type)
        if status_code is not None:
            headers = {"WWW-Authenticate": "Bearer"} if status_code == 401 else None
            return JSONResponse(
                {"detail": str(exc)},
                status_code=status_code,
                headers=headers,
            )

    logger.exception("Unhandled error", exc_info=exc)
    return JSONResponse({"detail": "Internal server error"}, status_code=500)


def register_error_handlers(app: FastAPI) -> None:
    for base in (DomainError, ApplicationError, PresentationError):
        app.add_exception_handler(base, _handle)
