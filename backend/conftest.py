"""Root-level conftest.py — sets required env vars BEFORE pytest collects tests.

app.core.config.Settings() is instantiated at import time, so the vars must
exist in os.environ before any app.* module is imported during collection.

Only DATABASE_URL and JWT_SECRET_KEY are required; all other settings now
have safe defaults in config.py.
"""

import os

_TEST_ENV = {
    "DATABASE_URL": "postgres://test:test@localhost:5432/singulari_test",
    "JWT_SECRET_KEY": "test-secret-key-not-used-in-production",
}

for key, value in _TEST_ENV.items():
    os.environ.setdefault(key, value)
