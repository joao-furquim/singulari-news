"""Root-level conftest.py — sets required env vars BEFORE pytest collects tests.

app.core.config.Settings() is instantiated at import time, so the vars must
exist in os.environ before any app.* module is imported during collection.
"""

import os

_TEST_ENV = {
    "DATABASE_URL": "postgres://test:test@localhost:5432/singulari_test",
    "JWT_SECRET_KEY": "test-secret-key-not-used-in-production",
    "JWT_ALGORITHM": "HS256",
    "REDIS_URL": "redis://localhost:6379",
    "RESEND_API_KEY": "re_test_key",
    "EMAIL_FROM": "test@singulari.com",
    "R2_ACCOUNT_ID": "test_account",
    "R2_ACCESS_KEY_ID": "test_access_key",
    "R2_SECRET_ACCESS_KEY": "test_secret",
    "R2_BUCKET_NAME": "test-bucket",
    "R2_PUBLIC_URL": "https://test.r2.dev",
    "AI_API_KEY": "test_ai_key",
    "AI_MODEL": "test-model",
}

for key, value in _TEST_ENV.items():
    os.environ.setdefault(key, value)
