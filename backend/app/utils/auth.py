"""
Passwords and tokens.

Passwords are never stored. We store a bcrypt *hash*: a scrambled version
that cannot be turned back into the password, but can be checked against a
password someone types. Even someone who steals the database cannot log in.

A token (JWT) is a signed string carrying the user's email and role. The
signature uses the server's secret key, so nobody can forge one. It expires
after the number of hours set in .env (24 by default).
"""

from datetime import datetime, timedelta, timezone

from jose import JWTError, jwt
from passlib.context import CryptContext

from app.config import settings

# "deprecated=auto" means: if we ever switch algorithms, old hashes still
# verify and get upgraded on next login.
_pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(plain: str) -> str:
    return _pwd_context.hash(plain)


def verify_password(plain: str, hashed: str) -> bool:
    return _pwd_context.verify(plain, hashed)


def create_access_token(*, email: str, role: str) -> str:
    """Build a signed token for this user. `sub` (subject) is the standard claim for who."""
    now = datetime.now(timezone.utc)
    payload = {
        "sub": email,
        "role": role,
        "iat": now,                                                          # issued at
        "exp": now + timedelta(hours=settings.access_token_expire_hours),   # expires
    }
    return jwt.encode(payload, settings.secret_key, algorithm=settings.jwt_algorithm)


def decode_access_token(token: str) -> dict | None:
    """
    Read a token back. Returns the payload, or None if the token is invalid,
    tampered with, or expired. Never raises: the caller decides what a bad
    token means (always a 401).
    """
    try:
        return jwt.decode(token, settings.secret_key, algorithms=[settings.jwt_algorithm])
    except JWTError:
        return None
