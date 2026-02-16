from django.urls import reverse

from rest_framework import status
from rest_framework.test import APITestCase

class EcapApiTest(APITestCase):
    def setUp(self) -> None:
        super().setUp()

    def test_east_and_north(self):
        """
        Tests geojson view returns at least 1 estate
        """
        url = '/ecap/estate/?east=2562165&north=1205258'
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        self.assertGreater(len(data['features']), 0)

    def test_east_north_and_buffer(self):
        """
        Tests geojson view returns at least more than 1 estate when buffer is given
        """
        url = '/ecap/estate/?east=2562165&north=1205258&buffer=50'
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        self.assertGreater(len(data['features']), 1)
        first_estate = data['features'][0]
        self.assertIn('cadastre', first_estate['properties'], 'Cadastre is given in answer')

    def test_estate_limit(self):
        """
        Tests geojson view returns at no more than 200 estates when buffer huge
        """
        url = '/ecap/estate/?east=2562165&north=1205258&buffer=1000'
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        self.assertEqual(len(data['features']), 200)

    def test_sinistres(self):
        """
        Tests json of sinistres is a list
        """
        url = reverse('ecap-intra-sinistres-exceptionnels')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        self.assertGreater(len(data), 2)

    def test_preavis(self):
        """
        Tests json of preavis is a list
        """
        url = reverse('ecap-intra-preavis')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        self.assertGreater(len(data), 1)
