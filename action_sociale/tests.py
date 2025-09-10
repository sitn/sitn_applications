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
        url = reverse("gsr_intersection")

        # A point in Neuchâtel
        geojson_point = {
            "type": "FeatureCollection",
            "features": [
                {
                    "type": "Feature",
                    "geometry": {
                        "type": "Point",
                        "srid": "2056",
                        "coordinates": [2558480, 1204290],
                    },
                    "properties": {"nom": "Le magnifique point"},
                }
            ],
        }

        # A rectangle covering two different GSR areas but mostly Neuchâtel
        geojson_polygon = {
            "type": "FeatureCollection",
            "features": [
                {
                    "type": "Feature",
                    "geometry": {
                        "type": "Polygon",
                        "srid": "2056",
                        "coordinates": [
                            [
                                [2559570, 1204856],
                                [2559445, 1205856],
                                [2556662, 1205828],
                                [2556613, 1204731],
                                [2559570, 1204856],
                            ]
                        ],
                    },
                    "properties": {"nom": "Le magnifique poylgone"},
                }
            ],
        }

        for geojson in [geojson_point, geojson_polygon]:
            response = self.client.post(
                url, json.dumps(geojson), content_type="application/json"
            )

            self.assertEqual(response.status_code, 200)

            resp_json = json.loads(response.content.decode("utf-8"))

            self.assertEqual(len(resp_json["features"]), 1)
            self.assertEqual(
                resp_json["features"][0]["properties"]["nom_gsr"], "GSR Neuchâtel"
            )
