"""Unit tests for require_role() FastAPI dependency."""

import pytest
from fastapi import HTTPException

from app.core.dependencies import require_role
from app.schemas.user import UserOut

# ── require_role("admin") ─────────────────────────────────────────────────────


async def test_require_role_admin_allows_admin(sample_admin: UserOut) -> None:
    """Admin user satisfies require_role("admin")."""
    check_role = require_role("admin")
    result = await check_role(current_user=sample_admin)
    assert result is sample_admin


async def test_require_role_admin_denies_user(sample_user: UserOut) -> None:
    """Regular user is denied by require_role("admin") with 403."""
    check_role = require_role("admin")
    with pytest.raises(HTTPException) as exc_info:
        await check_role(current_user=sample_user)
    assert exc_info.value.status_code == 403
    assert "Access denied" in exc_info.value.detail


async def test_require_role_root_allows_everything(sample_root: UserOut) -> None:
    """Root user bypasses all role checks regardless of required roles."""
    # "admin" is required but root should always pass
    check_role = require_role("admin")
    result = await check_role(current_user=sample_root)
    assert result is sample_root


async def test_require_role_root_allows_reviewer_restricted_route(
    sample_root: UserOut,
) -> None:
    """Root passes even reviewer-restricted routes."""
    check_role = require_role("reviewer")
    result = await check_role(current_user=sample_root)
    assert result is sample_root


# ── require_role("reviewer", "admin") ────────────────────────────────────────


async def test_require_role_multi_allows_reviewer(sample_user: UserOut) -> None:
    """Reviewer role satisfies require_role('reviewer', 'admin')."""
    from app.schemas.user import UserOut as _UserOut
    from datetime import datetime
    from uuid import uuid4

    reviewer = _UserOut(
        id=uuid4(),
        name="Rev",
        email="rev@test.com",
        avatar_url=None,
        locale="en",
        role="reviewer",
        must_change_password=False,
        created_at=datetime(2026, 1, 1),
    )
    check_role = require_role("reviewer", "admin")
    result = await check_role(current_user=reviewer)
    assert result is reviewer


async def test_require_role_multi_denies_plain_user(sample_user: UserOut) -> None:
    """Plain user is denied by require_role('reviewer', 'admin')."""
    check_role = require_role("reviewer", "admin")
    with pytest.raises(HTTPException) as exc_info:
        await check_role(current_user=sample_user)
    assert exc_info.value.status_code == 403


# ── error detail content ──────────────────────────────────────────────────────


async def test_require_role_403_detail_contains_required_role(
    sample_user: UserOut,
) -> None:
    """The 403 detail message names the required role."""
    check_role = require_role("admin")
    with pytest.raises(HTTPException) as exc_info:
        await check_role(current_user=sample_user)
    assert "admin" in exc_info.value.detail


async def test_require_role_returns_user_object_on_success(
    sample_admin: UserOut,
) -> None:
    """The dependency returns the current_user object unchanged on success."""
    check_role = require_role("admin")
    result = await check_role(current_user=sample_admin)
    assert result.id == sample_admin.id
    assert result.role == "admin"
