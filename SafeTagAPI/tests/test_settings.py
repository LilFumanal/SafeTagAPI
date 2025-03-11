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