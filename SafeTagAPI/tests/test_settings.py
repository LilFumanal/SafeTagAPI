from datetime import timedelta
import pytest
from django.conf import settings
from django.test import override_settings

@pytest.mark.django_db
@override_settings(DEBUG=True)
def test_debug_mode():
    assert settings.DEBUG is True

@pytest.mark.django_db
@override_settings(DEBUG=False)
def test_debug_mode_false():
    assert settings.DEBUG is False

@pytest.mark.django_db
def test_secret_key():
    assert hasattr(settings, 'SECRET_KEY')
    assert isinstance(settings.SECRET_KEY, str)

@pytest.mark.django_db
def test_allowed_hosts():
    assert hasattr(settings, 'ALLOWED_HOSTS')
    assert isinstance(settings.ALLOWED_HOSTS, list)

@pytest.mark.django_db
def test_installed_apps():
    assert hasattr(settings, 'INSTALLED_APPS')
    assert isinstance(settings.INSTALLED_APPS, list)
    
@pytest.mark.django_db
def test_rest_framework_settings():
    assert hasattr(settings, 'REST_FRAMEWORK')
    assert 'DEFAULT_AUTHENTICATION_CLASSES' in settings.REST_FRAMEWORK
    assert 'rest_framework_simplejwt.authentication.JWTAuthentication' in settings.REST_FRAMEWORK['DEFAULT_AUTHENTICATION_CLASSES']
    
@pytest.mark.django_db
def test_simple_jwt_settings():
    assert hasattr(settings, 'SIMPLE_JWT')
    assert settings.SIMPLE_JWT['ACCESS_TOKEN_LIFETIME'] == timedelta(minutes=5)
    assert settings.SIMPLE_JWT['REFRESH_TOKEN_LIFETIME'] == timedelta(days=1)
    assert settings.SIMPLE_JWT['ALGORITHM'] == 'HS256'
    assert settings.SIMPLE_JWT['SIGNING_KEY'] == settings.SECRET_KEY
    
@pytest.mark.django_db
def test_cors_settings():
    assert hasattr(settings, 'CORS_ALLOWED_ORIGINS')
    assert "http://localhost:4200" in settings.CORS_ALLOWED_ORIGINS
    assert "https://your-production-domain.com" in settings.CORS_ALLOWED_ORIGINS
    assert hasattr(settings, 'CORS_ALLOW_HEADERS')
    assert "content-type" in settings.CORS_ALLOW_HEADERS
    assert "authorization" in settings.CORS_ALLOW_HEADERS
    assert "x-csrftoken" in settings.CORS_ALLOW_HEADERS