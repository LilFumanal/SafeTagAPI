from aiocache import caches
import aiohttp
import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from django.test import TestCase
from SafeTagAPI.lib.esante_api_treatement import (
    get_all_practitioners,
    get_organization_info,
    get_practitioner_details,
    collect_addresses
)

class TestEsanteAPITreatment(TestCase):
    
    @pytest.mark.django_db
    @pytest.mark.asyncio
    @patch('aiohttp.ClientSession.get')
    async def test_get_organization_info(self, mock_get):
        mock_response = MagicMock()
        mock_response.status = 200
        mock_response.json = AsyncMock(return_value={
            "api_id": "123",
            "name": "Test Organization",
            "address": [{"city": "Test City", "postalCode": "12345"}]
        })
        mock_get.return_value.__aenter__.return_value = mock_response

        org_reference = "123"
        organization_info, org_addresses = await get_organization_info(org_reference)

        assert organization_info["name"] == "Test Organization"
        assert org_addresses[0]["city"] == "Test City"

    @pytest.mark.django_db
    @pytest.mark.asyncio
    @patch('SafeTagAPI.lib.esante_api_treatement.aiohttp.ClientSession.get')
    async def test_get_all_practitioners_success(self, mock_get):
        mock_response = MagicMock()
        mock_response.status = 200
        async def mock_json():
            return {
                "entry": [
                    {"resource": {"id": "practitioner123", "organization": {"reference": "123"}}}
                ],
                "link": [{"relation": "next", "url": "http://next-page-url"}]
            }
        mock_response.json = mock_json
        mock_get.return_value.__aenter__.return_value = mock_response

        with patch('SafeTagAPI.lib.esante_api_treatement.process_practitioner_entry', return_value={"api_id": "123"}):
            practitioners_list, next_page = await get_all_practitioners("http://test-url")
            self.assertIsInstance(practitioners_list, list)
            self.assertEqual(len(practitioners_list), 1)
            self.assertEqual(practitioners_list[0]["api_id"], "123")
            self.assertEqual(next_page, "http://next-page-url")

    @pytest.mark.django_db
    @pytest.mark.asyncio
    async def test_get_all_practitioners_cache(self):
        cache = caches.get('default')
        await cache.clear()
        mock_response = {
            "entry": [{"resource": {"id": "456", "organization": {"reference": "123"}}}],
            "link": [{"relation": "next", "url": "http://next-page-url"}]
        }
        
        with patch("aiohttp.ClientSession.get") as mock_get, \
            patch('SafeTagAPI.lib.esante_api_treatement.get_organization_info', return_value=(None, None)):
            mock_get.return_value.__aenter__.return_value.json = AsyncMock(return_value=mock_response)
            result1, next_page1 = await get_all_practitioners("http://test-url")
            mock_get.assert_called_once()
            self.assertIsInstance(result1, list)
            self.assertEqual(next_page1, "http://next-page-url")
            
            result2, next_page2 = await get_all_practitioners("http://test-url")
            mock_get.assert_called_once()
            self.assertEqual(result2, result1)
            self.assertEqual(next_page2, next_page1)
            
            result3, next_page3 = await get_all_practitioners("http://test-url?page=2")
            self.assertEqual(mock_get.call_count, 2)
        
        await cache.clear()

    async def test_collect_addresses(self):
        addresses = [{"city": "CityA", "postalCode": "12345"}, {"city": "CityB", "postalCode": "67890"}]
        collected_addresses = await collect_addresses(addresses)
        self.assertEqual(len(collected_addresses), 2)
        self.assertEqual(collected_addresses[0]["city"], "CityA")
        self.assertEqual(collected_addresses[1]["city"], "CityB")