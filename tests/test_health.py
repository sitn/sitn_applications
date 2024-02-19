import pytest
from unittest import TestCase

class TestHealth(TestCase):
    @pytest.fixture(autouse=True, scope="function")
    def _setUp(self, init_config):
        self.client = init_config.get("client")
        self.url = f"{init_config.get('base_url')}/health"

    def test_health_get(self):
        """
        Tests base URL
        """
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)

    def test_doctors_list(self):
        """
        All doctors
        """
        response = self.client.get(f"{self.url}/doctors")
        self.assertEqual(response.status_code, 200)

    def test_doctors_geojson(self):
        """
        GeoJSON view of all doctors
        """
        response = self.client.get(f"{self.url}/doctors/as_geojson")
        self.assertEqual(response.status_code, 200)