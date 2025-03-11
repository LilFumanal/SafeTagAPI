import pytest
from unittest.mock import patch
from django.core.management import call_command
from io import StringIO
from SafeTagAPI.lib.pathologies_dictionary import DSM5Pathologies

@pytest.mark.django_db
@patch('SafeTagAPI.models.review_model.Pathologie.objects.get_or_create')
def test_pathologies_command(mock_get_or_create):
    out = StringIO()
    call_command('pathologies', stdout=out)
    
    # Check that get_or_create was called for each item in DSM5Pathologies
    assert mock_get_or_create.call_count == len(DSM5Pathologies)
    
    for name, description in DSM5Pathologies.items():
        mock_get_or_create.assert_any_call(name=name, description=description)
    
    assert "Successfully initialized pathologies" in out.getvalue()

@pytest.mark.django_db
@patch('SafeTagAPI.models.review_model.Pathologie.objects.get_or_create')
def test_handle_no_errors(mock_get_or_create):
    try:
        call_command('pathologies')
    except Exception as e:
        pytest.fail(f"pathologies command raised an exception: {e}")

@pytest.mark.django_db
@patch('SafeTagAPI.models.review_model.Pathologie.objects.get_or_create')
def test_handle_output(mock_get_or_create):
    out = StringIO()
    call_command('pathologies', stdout=out)
    assert "Successfully initialized pathologies" in out.getvalue()