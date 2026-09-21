"""
backend/tests/test_auth.py

Pytest test suite for the Clerk JWT authentication layer.

Strategy:
  - We mint our own RS256 JWT tokens (using a locally generated key pair)
    and monkey-patch the JWKS cache so the auth module trusts them.
  - We bypass the real Qdrant / DB layer using lifespan override + mocked
    dependency injection where needed.
  - The test client is AsyncClient against the FastAPI app.

Run with:
    cd backend
    pip install pytest pytest-asyncio httpx cryptography python-jose[cryptography]
    pytest tests/test_auth.py -v
"""

from __future__ import annotations

import time
from typing import Any
from unittest.mock import patch, AsyncMock

import pytest
import pytest_asyncio
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.backends import default_backend
from jose import jwk as jose_jwk, jwt
from httpx import AsyncClient, ASGITransport

# ── Generate a throw-away RSA key pair for signing test tokens ────────────────

_private_key = rsa.generate_private_key(
    public_exponent=65537,
    key_size=2048,
    backend=default_backend(),
)
_public_key = _private_key.public_key()

# Build a JWK dict from the public key so we can mock the JWKS endpoint
_jwk_obj = jose_jwk.construct(_public_key, algorithm="RS256")
_TEST_KID = "test-key-id-001"
_TEST_JWKS = {
    "keys": [
        {**_jwk_obj.to_dict(), "kid": _TEST_KID, "use": "sig", "alg": "RS256"}
    ]
}

_TEST_ISSUER = "https://test-clerk-issuer.example.com"


def _mint_token(
    sub: str = "user_test123",
    org_role: str = "",
    issuer: str = _TEST_ISSUER,
    exp_offset: int = 3600,
) -> str:
    """Return a signed JWT that will pass verification when JWKS is mocked."""
    now = int(time.time())
    claims = {
        "sub": sub,
        "iss": issuer,
        "iat": now,
        "nbf": now,
        "exp": now + exp_offset,
    }
    if org_role:
        claims["org_role"] = org_role

    return jwt.encode(
        claims,
        _private_key,
        algorithm="RS256",
        headers={"kid": _TEST_KID},
    )


# ── App fixture with JWKS mocked ─────────────────────────────────────────────

@pytest.fixture(autouse=True)
def mock_jwks_and_settings(monkeypatch):
    """
    Patch the JWKS cache and settings so auth works without network calls
    and without real Clerk credentials.
    """
    import core.auth as auth_mod
    import core.config as cfg_mod

    # Patch the cache directly so _get_jwks() returns our test JWKS
    monkeypatch.setattr(auth_mod, "_JWKS_CACHE", _TEST_JWKS)
    monkeypatch.setattr(auth_mod, "_JWKS_FETCHED_AT", time.monotonic())

    # Patch settings so clerk_issuer matches our test tokens
    monkeypatch.setattr(cfg_mod.settings, "clerk_jwks_url", "http://mock/jwks.json")
    monkeypatch.setattr(cfg_mod.settings, "clerk_issuer", _TEST_ISSUER)
    monkeypatch.setattr(cfg_mod.settings, "clerk_audience", "")


@pytest_asyncio.fixture
async def client():
    """AsyncClient pointing at the FastAPI app."""
    # Override the lifespan to skip DB/Qdrant initialization
    from contextlib import asynccontextmanager
    from unittest.mock import AsyncMock, patch

    @asynccontextmanager
    async def _noop_lifespan(app):
        yield

    with (
        patch("main.create_tables", new_callable=AsyncMock),
        patch("main.ensure_collection_exists", return_value=None),
        patch("main.start_scheduler", return_value=None),
        patch("main.stop_scheduler", return_value=None),
    ):
        # Import after patching to get the patched version
        from main import app
        app.router.lifespan_context = _noop_lifespan

        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as ac:
            yield ac


# ── Helper ────────────────────────────────────────────────────────────────────

def _auth_header(token: str) -> dict:
    return {"Authorization": f"Bearer {token}"}


# ════════════════════════════════════════════════════════════════════════════
# Tests
# ════════════════════════════════════════════════════════════════════════════

class TestNoToken:
    """Requests with no Authorization header must return 401."""

    @pytest.mark.asyncio
    async def test_regulations_no_token(self, client: AsyncClient):
        resp = await client.get("/api/regulations/")
        assert resp.status_code == 401

    @pytest.mark.asyncio
    async def test_impact_no_token(self, client: AsyncClient):
        resp = await client.get("/api/impact/heatmap")
        assert resp.status_code == 401

    @pytest.mark.asyncio
    async def test_rag_no_token(self, client: AsyncClient):
        resp = await client.post("/api/rag/explain", json={"question": "test"})
        assert resp.status_code == 401

    @pytest.mark.asyncio
    async def test_analytics_no_token(self, client: AsyncClient):
        resp = await client.get("/api/analytics/risk-heatmap")
        assert resp.status_code == 401

    @pytest.mark.asyncio
    async def test_ingest_no_token(self, client: AsyncClient):
        resp = await client.post("/api/ingest/upload")
        assert resp.status_code == 401


class TestInvalidToken:
    """Malformed / invalid / expired tokens must return 401."""

    @pytest.mark.asyncio
    async def test_garbage_token(self, client: AsyncClient):
        resp = await client.get(
            "/api/regulations/", headers={"Authorization": "Bearer not.a.token"}
        )
        assert resp.status_code == 401

    @pytest.mark.asyncio
    async def test_expired_token(self, client: AsyncClient):
        expired = _mint_token(exp_offset=-10)  # already expired 10s ago
        resp = await client.get(
            "/api/regulations/", headers=_auth_header(expired)
        )
        assert resp.status_code == 401

    @pytest.mark.asyncio
    async def test_wrong_issuer(self, client: AsyncClient):
        bad_issuer_token = _mint_token(issuer="https://evil.attacker.com")
        resp = await client.get(
            "/api/regulations/", headers=_auth_header(bad_issuer_token)
        )
        assert resp.status_code == 401


class TestValidNonAdminToken:
    """Valid user tokens must be accepted for normal routes, rejected on admin routes."""

    @pytest.mark.asyncio
    async def test_user_can_access_regulations(
        self, client: AsyncClient, monkeypatch
    ):
        """
        A valid user token should pass auth on GET /api/regulations/.
        We mock the DB call so we don't need a real database.
        """
        from routers import regulations as reg_router
        import core.database as db_mod

        # Patch the DB to return an empty list
        async def _fake_execute(*args, **kwargs):
            class FakeResult:
                def scalars(self):
                    return self
                def all(self):
                    return []
            return FakeResult()

        monkeypatch.setattr(db_mod, "get_db", lambda: None)

        token = _mint_token(org_role="org:member")
        resp = await client.get("/api/regulations/", headers=_auth_header(token))
        # 401 or 403 would indicate auth failure; 200/422/500 mean auth passed
        assert resp.status_code != 401
        assert resp.status_code != 403

    @pytest.mark.asyncio
    async def test_non_admin_cannot_ingest(self, client: AsyncClient):
        """Non-admin users must receive 403 on admin-only endpoints."""
        token = _mint_token(org_role="org:member")
        resp = await client.post(
            "/api/ingest/upload",
            headers=_auth_header(token),
            files={"file": ("test.pdf", b"%PDF-1.4", "application/pdf")},
        )
        assert resp.status_code == 403

    @pytest.mark.asyncio
    async def test_non_admin_cannot_regulation_ingest(self, client: AsyncClient):
        token = _mint_token(org_role="org:member")
        resp = await client.post(
            "/api/regulations/ingest",
            headers=_auth_header(token),
            json={"title": "Test", "text": "Body", "category": "Test"},
        )
        assert resp.status_code == 403

    @pytest.mark.asyncio
    async def test_non_admin_cannot_sync_all(self, client: AsyncClient):
        token = _mint_token(org_role="org:member")
        resp = await client.post(
            "/api/regulations/sync/all", headers=_auth_header(token)
        )
        assert resp.status_code == 403


class TestAdminToken:
    """Org admin tokens must be accepted on admin routes (actual DB calls mocked)."""

    @pytest.mark.asyncio
    async def test_admin_can_reach_ingest(self, client: AsyncClient, monkeypatch):
        """
        Admin token should pass 401/403 checks on POST /api/ingest/upload.
        The endpoint may still return 422 (no file) or 500 (no Qdrant), but
        not 401 or 403.
        """
        token = _mint_token(org_role="org:admin")
        resp = await client.post(
            "/api/ingest/upload",
            headers=_auth_header(token),
            # Intentionally omitting the file to get a 422, proving auth passed
        )
        # Auth checks pass; FastAPI will reject the missing file with 422
        assert resp.status_code not in (401, 403)

    @pytest.mark.asyncio
    async def test_admin_can_reach_sync_all(self, client: AsyncClient, monkeypatch):
        """Admin token passes auth on sync/all endpoint."""
        # Patch the heavy sync function
        monkeypatch.setattr(
            "main.sync_all_jurisdictions",
            AsyncMock(return_value={"total": 0}),
        )
        from core.database import get_db as _get_db
        import core.database as db_mod

        class FakeSession:
            async def __aenter__(self): return self
            async def __aexit__(self, *a): pass

        token = _mint_token(org_role="org:admin")
        resp = await client.post(
            "/api/regulations/sync/all", headers=_auth_header(token)
        )
        assert resp.status_code not in (401, 403)


class TestPublicEndpoints:
    """Health and root endpoints must remain fully public."""

    @pytest.mark.asyncio
    async def test_health_no_token(self, client: AsyncClient):
        resp = await client.get("/health")
        assert resp.status_code == 200

    @pytest.mark.asyncio
    async def test_root_no_token(self, client: AsyncClient):
        resp = await client.get("/")
        assert resp.status_code == 200
