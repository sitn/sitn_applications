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

    def test_parcel_dependencies(self):
        """
        This test just checks a PPE part (Tivoli 22)
        """
        url = "/registre_foncier/parcel/dependencies"
        response = self.client.get(url, query_params={"cadastre": "1", "parcel": "15176/A"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("data", response.json())
        data = response.json()['data']
        if data:
            self.assertIn("valid", data)
            self.assertTrue(data["valid"])
            self.assertEqual(len(data["data"]["parents"]), 1)
