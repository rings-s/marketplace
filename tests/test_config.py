def test_settings_loads():
    from app.config import settings
    assert settings.PLATFORM_FEE_PERCENT == 1.0
    assert settings.ACCESS_TOKEN_EXPIRE_MINUTES == 15
