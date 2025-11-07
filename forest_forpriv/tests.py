from django.urls import reverse

from rest_framework.test import APITestCase
from forest_forpriv.models import Fo02Cantonnement

from json import dumps


class ForestForpriv(APITestCase):
    
    def setUp(self) -> None:
        super().setUp()
    
    def test_intersection(self):
        url = reverse('forpriv-intersection')
        body = {
            "type": "FeatureCollection",
            "features": [{
                "type": "Feature",
                "geometry": {
                    "type": "Polygon",
                    "coordinates": [[[2543686,1199046],[2543619,1198960],[2543727,1198951],[2543788,1199003],[2543686,1199046]]]
                }
            }]
        }
        response = self.client.post(url, dumps(body), content_type='application/json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()['features']), 3)


    def test_multiple_intersection(self):
        """ Tests that when polygon intersects multiple features, the most relevant (by covered area) is returned"""
        cantonnement_to_test = Fo02Cantonnement.objects.get(geom__intersects='SRID=2056;POINT(2558696 1212700)')
        url = reverse('forpriv-intersection')
        body = {
            "type": "FeatureCollection",
            "features": [{
                "type": "Feature",
                "geometry": {
                    "type": "Polygon",
                    "coordinates": [[[2558306, 1212612], [2558488, 1213146], [2559116, 1212688], [2558306, 1212612]]]
                }
            }]
        }
        response = self.client.post(url, dumps(body), content_type='application/json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['features'][1]['properties']['titulaire'], cantonnement_to_test.titulaire)
