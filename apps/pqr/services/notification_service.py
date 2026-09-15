import threading
from typing import Protocol

import httpx
from django.conf import settings

from apps.common.logging import get_logger

logger = get_logger(__name__)


class NotificationPort(Protocol):
    def send(self, *, subject: str, to_email: str, body: str, metadata: dict | None = None) -> None:
        ...


class LoggingNotifier:
    """Fallback when EMAIL_API_KEY is missing."""

    def send(self, *, subject: str, to_email: str, body: str, metadata: dict | None = None) -> None:
        logger.info(
            "notification_logged",
            subject=subject,
            to_email=to_email,
            body=body,
            metadata=metadata or {},
        )


class HttpEmailNotifier:
    """Sends email via external HTTP API (e.g. Resend)."""

    def __init__(self, *, api_key: str, api_url: str, from_email: str):
        self._api_key = api_key
        self._api_url = api_url
        self._from_email = from_email

    def send(self, *, subject: str, to_email: str, body: str, metadata: dict | None = None) -> None:
        thread = threading.Thread(
            target=self._send_sync,
            kwargs={
                "subject": subject,
                "to_email": to_email,
                "body": body,
                "metadata": metadata,
            },
            daemon=True,
        )
        thread.start()

    def _send_sync(
        self,
        *,
        subject: str,
        to_email: str,
        body: str,
        metadata: dict | None = None,
    ) -> None:
        payload = {
            "from": self._from_email,
            "to": [to_email],
            "subject": subject,
            "text": body,
        }
        try:
            response = httpx.post(
                self._api_url,
                headers={
                    "Authorization": f"Bearer {self._api_key}",
                    "Content-Type": "application/json",
                },
                json=payload,
                timeout=10.0,
            )
            response.raise_for_status()
            logger.info(
                "notification_sent",
                to_email=to_email,
                subject=subject,
                metadata=metadata or {},
                status_code=response.status_code,
            )
        except httpx.HTTPError as exc:
            logger.error(
                "notification_failed",
                to_email=to_email,
                subject=subject,
                error=str(exc),
                metadata=metadata or {},
            )


def build_notifier() -> NotificationPort:
    if not getattr(settings, "NOTIFICATIONS_ENABLED", True):
        return LoggingNotifier()
    api_key = getattr(settings, "EMAIL_API_KEY", "") or ""
    if not api_key:
        return LoggingNotifier()
    return HttpEmailNotifier(
        api_key=api_key,
        api_url=settings.EMAIL_API_URL,
        from_email=settings.EMAIL_FROM,
    )
