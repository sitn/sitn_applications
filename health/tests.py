from django.utils import timezone

from rest_framework import status
from rest_framework.test import APITestCase

from health.models import St20AvailableDoctors, St22DoctorChangeSuggestion

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
        Emails should be sent, timeout should work
        """
        doctor = St20AvailableDoctors.objects.first()
        url = f'/health/doctors/{doctor.pk}/request_change/'
        response = self.client.post(url, {
            "login_email": "wrong.email@somwhere.com"
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        doctor = St20AvailableDoctors.objects.get(pk=doctor.pk)
        self.assertIsNotNone(doctor.guid_requested_when, 'A date should be present')
        response = self.client.post(url, {
            "login_email": "wrong.email@somwhere.com"
        })
        self.assertEqual(response.status_code, status.HTTP_429_TOO_MANY_REQUESTS)

    def test_doctor_put_changes(self):
        """
        Doctor submits his changes
        """
        doctor = St20AvailableDoctors.objects.first()
        doctor.prepare_for_edit()
        doctor.guid_requested_when = timezone.now()
        doctor.availability = "Unknown"
        doctor.is_rsn_member = None
        doctor.save()

        url = f'/health/doctors/edit/{doctor.edit_guid}/'
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        new_data = {
            "availability": "Available",
            "availability_conditions": "Only nice people",
            "spoken_languages": [
                "Français",
                "Chinois"
            ],
            "has_parking": True,
            "has_disabled_access": False,
            "has_lift": True,
            "public_phone": "+41 32 321 00 00",
            "public_first_name": "Heldér Iñaki",
            "is_rsn_member": False
        }
        response = self.client.put(url, new_data)
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)
        doctor = St20AvailableDoctors.objects.get(pk=doctor.pk)
        for key in new_data.keys():
            doctor_value = getattr(doctor, key, None)
            if isinstance(new_data[key], list):
                self.assertEqual(set(doctor_value), set(new_data[key]))
            else:
                self.assertEqual(doctor_value, new_data[key], 'Data should have been updated')
        self.assertIsNone(doctor.edit_guid, 'edit_guid should have been deleted by the update')
        self.assertIsNone(doctor.guid_requested_when)
        self.assertAlmostEqual(timezone.now(), doctor.last_edit, delta=timezone.timedelta(minutes=1))
        
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND, 'It is no longer accessible')

    def test_doctor_put_changes_email_phone(self):
        """
        Doctor submits his new email and hides phone
        """
        doctor = St20AvailableDoctors.objects.first()
        doctor.prepare_for_edit()
        doctor.guid_requested_when = timezone.now()
        doctor.availability = "Unknown"
        doctor.login_email = "wrong_email@example.com"
        doctor.save()

        url = f'/health/doctors/edit/{doctor.edit_guid}/'
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        new_data = {
            "spoken_languages": [
                "Français"
            ],
            "has_parking": True,
            "has_disabled_access": False,
            "has_lift": True,
            "public_phone": "",
            "is_rsn_member": False
        }
        response = self.client.put(url, new_data)
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)
        doctor = St20AvailableDoctors.objects.get(pk=doctor.pk)
        self.assertEqual(doctor.public_phone, "", "Phone is empty")
        self.assertIsNone(doctor.edit_guid, 'edit_guid should have been deleted by the update')
        self.assertIsNone(doctor.guid_requested_when)
        self.assertAlmostEqual(timezone.now(), doctor.last_edit, delta=timezone.timedelta(minutes=1))
        
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND, 'It is no longer accessible')

    def test_suggest_doctor_changes(self):
        """
        An anonymous user is able to suggest changes to the app
        """
        doctor = St20AvailableDoctors.objects.first()
        St22DoctorChangeSuggestion.objects.filter(doctor__pk=doctor.pk).all().delete()

        suggestion = {
            "doctor": doctor.pk,
            "availability": "Available",
        }
        url = f'/health/doctors/suggest'
        response = self.client.post(url, suggestion)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED, 'First suggestion is ok')
        self.assertEqual(
            St22DoctorChangeSuggestion.objects.filter(doctor__pk=doctor.pk, is_done=False).count(),
            1,
            'One suggestions in db'
        )
        response = self.client.post(url, suggestion)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED, 'Second suggestion is ok')
        self.assertEqual(
            St22DoctorChangeSuggestion.objects.filter(doctor__pk=doctor.pk, is_done=False).count(),
            2,
            'Two suggestions in db'
        )
        response = self.client.post(url, suggestion)
        response = self.client.post(url, suggestion)
        self.assertEqual(
            response.status_code,
            status.HTTP_429_TOO_MANY_REQUESTS,
            'Do not let too many suggestions on same doctor'
        )