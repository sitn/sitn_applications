from django.test import SimpleTestCase
from django.conf import settings
from django.test import Client
from django.urls import reverse

from json import dumps

"""
  We got quite a problem currently, because without managing the tables
  the django framework cannot mount the DB.

  -> Check what is done in the geoportal and try to make similar tests.
  (TODO)
"""

# class ForestForpriv(SimpleTestCase):
    
#     def setUp(self):
#         # Every test needs a client.
#         self.client = Client()
    
#     def test_intersection(self):
#         url = reverse('forpriv-intersection')
#         body = {
#             "type": "FeatureCollection",
#             "features": [{
#                 "type": "Feature",
#                 "geometry": {
#                     "type": "Polygon",
#                     "coordinates": [[[2543686,1199046],[2543619,1198960],[2543727,1198951],[2543788,1199003],[2543686,1199046]]]
#                 }
#             }]
#         }
#         response = self.client.post(url, body)

#         # Check that route is responding
#         self.assertEqual(response.status_code, 200)

#         # Check GeoJson content



        