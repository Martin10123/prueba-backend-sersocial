from apps.accounts.models import User


class UserRepository:
    def get_by_email(self, email: str) -> User | None:
        return User.objects.filter(email__iexact=email).first()

    def get_by_id(self, user_id: int) -> User | None:
        return User.objects.filter(pk=user_id).first()
