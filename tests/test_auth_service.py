import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from app.services.auth import AuthService


@pytest.mark.asyncio
async def test_google_login_creates_new_user():
    mock_session = AsyncMock()
    service = AuthService(mock_session)

    mock_claims = {"sub": "google-123", "email": "test@example.com", "name": "Test User"}

    with patch("app.services.auth.verify_google_token", return_value=mock_claims):
        with patch.object(service.repo, "get_by_google_sub", return_value=None):
            with patch.object(service.repo, "get_by_email", return_value=None):
                mock_user = MagicMock()
                mock_user.id = "user-uuid"
                mock_user.role = "buyer"
                with patch.object(service.repo, "create", return_value=mock_user):
                    user, access, refresh = await service.google_login("fake-token")
                    assert user == mock_user
                    assert access
                    assert refresh


@pytest.mark.asyncio
async def test_google_login_links_existing_email_user():
    mock_session = AsyncMock()
    service = AuthService(mock_session)

    mock_claims = {"sub": "google-456", "email": "existing@example.com", "name": "Existing User"}
    existing_user = MagicMock()
    existing_user.id = "existing-uuid"
    existing_user.role = "buyer"
    existing_user.avatar_url = None

    with patch("app.services.auth.verify_google_token", return_value=mock_claims):
        with patch.object(service.repo, "get_by_google_sub", return_value=None):
            with patch.object(service.repo, "get_by_email", return_value=existing_user):
                with patch.object(service.repo, "update", return_value=None):
                    with patch.object(service.repo, "get", return_value=existing_user):
                        user, access, refresh = await service.google_login("fake-token")
                        assert user == existing_user
                        assert access
                        assert refresh
