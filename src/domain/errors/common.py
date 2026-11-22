from src.domain.errors.base import DomainError


class NotFoundError(DomainError):
    pass


class AlreadyExistsError(DomainError):
    pass
