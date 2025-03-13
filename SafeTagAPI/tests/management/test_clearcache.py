import pytest
from unittest.mock import patch
from django.core.management import call_command
from io import StringIO

@pytest.mark.django_db
@patch('django.core.caches.caches.clear')
def test_clear_cache(mock_clear):
    out = StringIO()
    call_command('clearcache', stdout=out)
    mock_clear.assert_called_once()
    assert "Successfully cleared caches" in out.getvalue()

@pytest.mark.django_db
@patch('django.core.caches.caches.clear')
def test_clear_cache_output(mock_clear):
    out = StringIO()
    call_command('clearcache', stdout=out)
    assert "Successfully cleared caches" in out.getvalue()

@pytest.mark.django_db
@patch('django.core.caches.caches.clear')
def test_clear_cache_no_errors(mock_clear):
    try:
        call_command('clearcache')
    except Exception as e:
        pytest.fail(f"clearcache command raised an exception: {e}")