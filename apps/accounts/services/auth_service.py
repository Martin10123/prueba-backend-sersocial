from apps.accounts.repositories import UserRepository
from apps.common.exceptions import NotFoundError, ValidationError
from apps.common.logging import get_logger

logger = get_logger(__name__)


class AuthService:
    def __init__(self, user_repository: UserRepository):
        self._users = user_repository

    def authenticate(self, email: str, password: str):
        user = self._users.get_by_email(email)
        if user is None or not user.check_password(password):
            logger.info("auth_failed", email=email)
            raise ValidationError("Credenciales inválidas.", code="invalid_credentials")
        if not user.is_active:
            raise ValidationError("Usuario inactivo.", code="inactive_user")
        logger.info("auth_success", user_id=user.id, rol=user.rol)
        return user

    def get_user(self, user_id: int):
        user = self._users.get_by_id(user_id)
        if user is None:
            raise NotFoundError("Usuario no encontrado.")
        return user
