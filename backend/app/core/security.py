import base64
import hashlib
import hmac
import json
import secrets
from datetime import datetime, timedelta, timezone
from typing import Optional


SECRET_KEY = "campus-market-demo-secret"
TOKEN_EXPIRE_HOURS = 24


def hash_password(password: str, salt: Optional[str] = None) -> str:
    salt = salt or secrets.token_hex(16)
    digest = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt.encode("utf-8"), 100_000)
    return f"{salt}${digest.hex()}"


def verify_password(password: str, password_hash: str) -> bool:
    salt, _ = password_hash.split("$", 1)
    return hmac.compare_digest(hash_password(password, salt), password_hash)


def create_token(user_id: int) -> str:
    expire_at = datetime.now(timezone.utc) + timedelta(hours=TOKEN_EXPIRE_HOURS)
    payload = {"user_id": user_id, "exp": int(expire_at.timestamp())}
    body = base64.urlsafe_b64encode(json.dumps(payload).encode("utf-8")).decode("utf-8").rstrip("=")
    signature = hmac.new(SECRET_KEY.encode("utf-8"), body.encode("utf-8"), hashlib.sha256).hexdigest()
    return f"{body}.{signature}"


def decode_token(token: str) -> Optional[dict]:
    try:
        body, signature = token.split(".", 1)
        expected = hmac.new(SECRET_KEY.encode("utf-8"), body.encode("utf-8"), hashlib.sha256).hexdigest()
        if not hmac.compare_digest(signature, expected):
            return None
        payload_raw = base64.urlsafe_b64decode(body + "=" * (-len(body) % 4))
        payload = json.loads(payload_raw.decode("utf-8"))
        if payload["exp"] < int(datetime.now(timezone.utc).timestamp()):
            return None
        return payload
    except Exception:
        return None
