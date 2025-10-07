from rest_framework import status
from rest_framework.test import APITestCase


class RoadsApiTest(APITestCase):
    def setUp(self) -> None:
        super().setUp()

    def test_axis_list(self):
        """
        /roads/axis/ returns a list of axis objects
        """
        url = "/roads/axis/"
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        self.assertIsInstance(data, list)
        if data:
            self.assertIn("asg_iliid", data[0])
            self.assertIn("asg_name", data[0])
            self.assertIn("sectors", data[0])

    def test_axis_filter(self):
        """
        /roads/axis/?search=... filters axis by asg_name
        """
        url = "/roads/axis/?search=Test"
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        for axis in data:
            self.assertIn("Test", axis["asg_name"])

    def test_sectors_list(self):
        """
        /roads/axis/<asg_iliid>/sectors/ returns sectors for axis
        """
        # Get an axis iliid from the list
        axis_url = "/roads/axis/"
        axis_response = self.client.get(axis_url)
        self.assertEqual(axis_response.status_code, status.HTTP_200_OK)
        axis_data = axis_response.json()
        if axis_data:
            asg_iliid = axis_data[0]["asg_iliid"]
            url = f"/roads/axis/{asg_iliid}/sectors/"
            response = self.client.get(url)
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            sectors = response.json()["results"]
            self.assertIsInstance(sectors, list)
            for sector in sectors:
                self.assertIn("sec_name", sector)
                self.assertIn("sec_length", sector)
                self.assertIn("sec_km", sector)
