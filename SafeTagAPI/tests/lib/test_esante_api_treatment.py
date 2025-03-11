import aiohttp
import pytest
from unittest.mock import patch, MagicMock
from SafeTagAPI.lib.esante_api_treatement import get_all_practitioners, get_organization_info, get_practitioner_details, collect_addresses

@pytest.mark.django_db
@pytest.mark.asyncio
@patch('SafeTagAPI.lib.esante_api_treatement.requests.get')
async def test_get_organization_info(mock_get):
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "id": "org123",
        "name": "Test Organization",
        "address": [{"city": "Test City", "postalCode": "12345"}]
    }
    mock_get.return_value = mock_response

    org_reference = "org123"
    organization_info, org_addresses = get_organization_info(org_reference)

    assert organization_info["name"] == "Test Organization"
    assert org_addresses[0]["city"] == "Test City"

@pytest.mark.django_db
@pytest.mark.asyncio
@patch('SafeTagAPI.lib.esante_api_treatement.aiohttp.ClientSession.get')
async def test_get_all_practitioners_success(mock_get):
    mock_response = MagicMock()
    mock_response.status = 200
    async def mock_json():
        return {
            "entry": [
                {
                    "resource": {
                        "id": "practitioner123",
                        "extension": [],
                        "organization": {"reference": "org123"},
                        "specialty": [],
                        "code": []
                    }
                }
            ],
            "link": [
                {
                    "relation": "next",
                    "url": "http://next-page-url"
                }
            ]
        }
    mock_response.json = mock_json
    mock_get.return_value.__aenter__.return_value = mock_response

    with patch('SafeTagAPI.lib.esante_api_treatement.process_practitioner_entry', return_value={"id": "practitioner123"}):
        practitioners_list, next_page = await get_all_practitioners("http://test-url")
        assert isinstance(practitioners_list, list)
        assert len(practitioners_list) == 1
        assert practitioners_list[0]["id"] == "practitioner123"
        assert next_page == "http://next-page-url"

@pytest.mark.django_db
@pytest.mark.asyncio
@patch('SafeTagAPI.lib.esante_api_treatement.aiohttp.ClientSession.get')
async def test_get_all_practitioners_http_error(mock_get):
    mock_response = MagicMock()
    mock_response.status = 404
    async def mock_text():
        return "Not Found"
    mock_response.text = mock_text
    mock_get.return_value.__aenter__.return_value = mock_response

    practitioners_list, next_page = await get_all_practitioners("http://test-url")
    assert isinstance(practitioners_list, str)
    assert practitioners_list.startswith("Erreur 404")
    assert next_page is None

@pytest.mark.django_db
@pytest.mark.asyncio
@patch('SafeTagAPI.lib.esante_api_treatement.aiohttp.ClientSession.get')
async def test_get_all_practitioners_client_error(mock_get):
    mock_get.side_effect = aiohttp.ClientError("Request failed")

    practitioners_list, next_page = await get_all_practitioners("http://test-url")
    assert isinstance(practitioners_list, str)
    assert practitioners_list.startswith("Request failed")
    assert next_page is None
        
def test_collect_addresses():
    addresses = [
        {"city": "CityA", "postalCode": "12345"},
        {"city": "CityB", "postalCode": "67890"}
    ]
    collected_addresses = collect_addresses(addresses)
    assert len(collected_addresses) == 2
    assert collected_addresses[0]["city"] == "CityA"
    assert collected_addresses[1]["city"] == "CityB"
    
@pytest.mark.django_db
@pytest.mark.asyncio
@patch('SafeTagAPI.lib.esante_api_treatement.aiohttp.ClientSession.get')
async def test_get_practitioner_details_success(mock_get):
    mock_response = MagicMock()
    mock_response.status = 200
    async def mock_json():
        return {
            "id": "practitioner123",
            "extension": [],
            "organization": {"reference": "Test Org"},
            "specialty": [],
            "code": []
        }
    mock_response.json = mock_json
    mock_get.return_value.__aenter__.return_value = mock_response

    with patch('SafeTagAPI.lib.esante_api_treatement.get_organization_info', return_value=({"name": "Test Org"}, [{"city": "Test City"}])):
        practitioner_details = await get_practitioner_details("practitioner123")
        assert isinstance(practitioner_details, dict)
        assert "name" in practitioner_details
        assert practitioner_details["name"] == "N/A"
        assert practitioner_details["organizations"][0]["name"] == "Test Org"

@pytest.mark.django_db
@pytest.mark.asyncio
@patch('SafeTagAPI.lib.esante_api_treatement.aiohttp.ClientSession.get')
async def test_get_practitioner_details_http_error(mock_get):
    mock_response = MagicMock()
    mock_response.status = 404
    async def mock_text():
        return "Not Found"
    mock_response.text = mock_text
    mock_get.return_value.__aenter__.return_value = mock_response

    practitioner_details = await get_practitioner_details("practitioner123")
    assert isinstance(practitioner_details, dict)
    assert "error" in practitioner_details
    assert practitioner_details["error"] == "HTTP error 404"
    assert practitioner_details["details"] == "Not Found"

@pytest.mark.django_db
@pytest.mark.asyncio
@patch('SafeTagAPI.lib.esante_api_treatement.aiohttp.ClientSession.get')
async def test_get_practitioner_details_client_error(mock_get):
    mock_get.side_effect = aiohttp.ClientError("Request failed")

    practitioner_details = await get_practitioner_details("practitioner123")
    assert isinstance(practitioner_details, dict)
    assert "error" in practitioner_details
    assert practitioner_details["error"] == "Request failed"
    assert "details" in practitioner_details