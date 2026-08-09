"""
Thin wrapper around Firebase Admin SDK for push delivery. Kept separate
from NotificationRepository so the Celery worker and the API layer share
one code path for actually sending a push.
"""
import json
import logging

from app.core.config import settings

logger = logging.getLogger(__name__)

_firebase_app = None


def _get_firebase_app():
    global _firebase_app
    if _firebase_app is None:
        import firebase_admin
        from firebase_admin import credentials

        if not settings.FCM_CREDENTIALS_JSON:
            raise RuntimeError("FCM_CREDENTIALS_JSON is not configured")

        cred = credentials.Certificate(json.loads(settings.FCM_CREDENTIALS_JSON))
        _firebase_app = firebase_admin.initialize_app(cred)
    return _firebase_app


def send_push(device_token: str, title: str, body: str) -> bool:
    """Returns True on success. Never raises — a failed push should not
    break the caller's flow (e.g. a check-in submission)."""
    try:
        from firebase_admin import messaging

        _get_firebase_app()
        message = messaging.Message(
            notification=messaging.Notification(title=title, body=body),
            token=device_token,
        )
        messaging.send(message)
        return True
    except Exception as e:  # noqa: BLE001 — push failures must never propagate
        logger.warning("Push notification failed: %s", e)
        return False
