"""Security utilities for password hashing and JWT token management.

Provides bcrypt-based password helpers and functions for creating and
decoding signed JWT tokens used for user authentication and password resets.
All token configuration (secret key, algorithm, expiry) is read from
``app.core.config.settings``.
"""

from datetime import datetime, timedelta, timezone

import bcrypt
from app.core.config import settings
from jose import jwt


def hash_password(plain_password: str) -> str:
    """Hash a plaintext password using bcrypt with a random salt.

    :param plain_password: The plaintext password to hash.
    :return: A bcrypt-hashed string safe for database storage.
    """
    return bcrypt.hashpw(plain_password.encode(), bcrypt.gensalt()).decode()


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a plaintext password against a stored bcrypt hash.

    :param plain_password: The plaintext password to check.
    :param hashed_password: The bcrypt hash retrieved from the database.
    :return: ``True`` if the password matches the hash, ``False`` otherwise.
    """
    return bcrypt.checkpw(plain_password.encode(), hashed_password.encode())


def create_access_token(subject: str) -> str:
    """Create a signed JWT access token for an authenticated user.

    The token payload contains ``sub`` (user UUID string), ``exp`` (expiry
    timestamp), and ``type="access"`` to distinguish it from reset tokens.

    :param subject: The user UUID string to embed as the token subject.
    :return: A signed JWT string valid for ``JWT_ACCESS_TOKEN_EXPIRE_MINUTES``.
    """
    expires_at = datetime.now(timezone.utc) + timedelta(
        minutes=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES
    )
    payload = {"sub": subject, "exp": expires_at, "type": "access"}
    return jwt.encode(
        payload, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM
    )


def create_reset_token(subject: str) -> str:
    """Create a signed JWT password-reset token.

    The token payload contains ``sub`` (user UUID string), ``exp`` (expiry
    timestamp), and ``type="reset"`` to distinguish it from access tokens.

    :param subject: The user UUID string to embed as the token subject.
    :return: A signed JWT string valid for ``JWT_RESET_TOKEN_EXPIRE_MINUTES``.
    """
    expires_at = datetime.now(timezone.utc) + timedelta(
        minutes=settings.JWT_RESET_TOKEN_EXPIRE_MINUTES
    )
    payload = {"sub": subject, "exp": expires_at, "type": "reset"}
    return jwt.encode(
        payload, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM
    )


def decode_token(token: str) -> dict:
    """Decode and verify a signed JWT token.

    :param token: The raw JWT string to decode.
    :return: The decoded payload dictionary (includes ``sub``, ``exp``, ``type``).
    :raises jose.JWTError: When the token is invalid, expired, or the signature
                           does not match.
    """
    return jwt.decode(
        token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM]
    )
