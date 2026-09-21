import pytest
from core.database import get_async_database_url, get_masked_url

def test_get_async_database_url_postgres():
    # Should convert postgres:// to postgresql+asyncpg://
    url = "postgres://user:pass@host.com/db"
    assert get_async_database_url(url) == "postgresql+asyncpg://user:pass@host.com/db"

def test_get_async_database_url_postgresql():
    # Should convert postgresql:// to postgresql+asyncpg://
    url = "postgresql://user:pass@host.com/db"
    assert get_async_database_url(url) == "postgresql+asyncpg://user:pass@host.com/db"

def test_get_async_database_url_already_async():
    # Should leave postgresql+asyncpg:// alone
    url = "postgresql+asyncpg://user:pass@host.com/db"
    assert get_async_database_url(url) == "postgresql+asyncpg://user:pass@host.com/db"

def test_get_async_database_url_sslmode_require():
    # Should convert sslmode=require to ssl=require
    url = "postgres://user:pass@host.com/db?sslmode=require"
    # Note: query parameters might be reordered by make_url, but we just check the output string.
    result = get_async_database_url(url)
    assert result.startswith("postgresql+asyncpg://user:pass@host.com/db")
    assert "?ssl=require" in result
    assert "sslmode" not in result

def test_get_async_database_url_sqlite():
    url = "sqlite:///./test.db"
    assert get_async_database_url(url) == "sqlite+aiosqlite:///./test.db"

def test_get_async_database_url_missing():
    with pytest.raises(ValueError, match="DATABASE_URL is not set or empty"):
        get_async_database_url("")
    with pytest.raises(ValueError, match="DATABASE_URL is not set or empty"):
        get_async_database_url(None)

def test_get_async_database_url_unsupported():
    with pytest.raises(ValueError, match="Unsupported database scheme: mysql"):
        get_async_database_url("mysql://user:pass@localhost/db")

def test_get_masked_url():
    url = "postgresql+asyncpg://user:supersecretpass@host.com/db"
    masked = get_masked_url(url)
    assert "supersecretpass" not in masked
    assert "***" in masked
