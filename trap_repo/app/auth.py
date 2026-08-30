"""JWT authentication module."""

import secrets
from datetime import datetime, timedelta, timezone

SECRET_KEY = None


def get_secret_key() -> str:
    global SECRET_KEY
    if SECRET_KEY is None:
        SECRET_KEY = secrets.token_hex(32)
    return SECRET_KEY


def create_token(user_id: str, role: str, expires_in: int = 3600) -> str:
    """Create a simple JWT-like token (base64-encoded JSON for demo)."""
    import base64
    import json

    payload = {
        "user_id": user_id,
        "role": role,
        "exp": (datetime.now(timezone.utc) + timedelta(seconds=expires_in)).isoformat(),
        "iat": datetime.now(timezone.utc).isoformat(),
    }
    message = json.dumps(payload)
    signature = secrets.token_hex(16)
    token_data = f"{base64.b64encode(message.encode()).decode()}.{signature}"
    return token_data


def decode_token(token: str) -> dict | None:
    """Decode and validate a token. Returns payload or None if invalid."""
    import base64
    import json

    try:
        parts = token.split(".")
        if len(parts) != 2:
            return None
        message = base64.b64decode(parts[0]).decode()
        payload = json.loads(message)
        exp = datetime.fromisoformat(payload["exp"])
        if datetime.now(timezone.utc) > exp:
            return None
        return payload
    except (ValueError, KeyError, json.JSONDecodeError):
        return None
