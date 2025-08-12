from django.test import Client
from unittest import TestCase
from django.urls import reverse
import json
# Create your tests here.

"""
Tests geojson of GSR intersection
"""

class GsrTestCase(TestCase):
    def setUp(self):
        self.client = Client()


    def test_gsr_intersection(self):
        url = reverse('gsr_intersection')

        geojson = {
            "type": "FeatureCollection",
            "features": [{
                "type": "Feature",
                "geometry": {
                    "type": "Point",
                    "srid": "2056",
                    "coordinates": [2558480, 1204290]    
                },
                "properties": {
                    "nom": "Le magnifique point"
                }
            }]
        }

        response = self.client.post(url,  json.dumps(geojson),
                                content_type="application/json")

        self.assertEqual(response.status_code, 200)

        resp_json = json.loads(response.content.decode("utf-8"))

        self.assertEqual(len(resp_json["features"]), 1)
        self.assertEqual(resp_json["features"][0]["properties"]["nom_gsr"], "GSR Neuchâtel")
