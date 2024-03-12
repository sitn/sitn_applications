from rest_framework import status
from rest_framework.test import APITestCase

from health.models import St20AvailableDoctors

class HealthApiTest(APITestCase):
    def setUp(self) -> None:
        super().setUp()

    def test_geojson_view(self):
        """
        Tests geojson view returns more than 100 results
        """
        url = '/health/doctors/as_geojson/'
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        self.assertGreater(len(data['features']), 100)

    def test_doctor_change_request(self):
        """
        Emails should be sent, timeout, should work
        """
        doctor = St20AvailableDoctors.objects.first()
        url = f'/health/doctors/{doctor.pk}/request_change/'
        print(url)
        response = self.client.post(url, {
            "login_email": "wrong.email@somwhere.com"
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)


