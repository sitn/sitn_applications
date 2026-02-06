from rest_framework import status
from rest_framework.test import APITransactionTestCase


class RegistreFoncierTest(APITransactionTestCase):
    databases = {"default", "terris"}

    def test_ttt(self):
        """
        /registre_foncier/ returns a chic type
        """
        url = "/registre_foncier/"
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        if data:
            self.assertIn("akt_name", data)
            self.assertIn("akt_vorname", data)
