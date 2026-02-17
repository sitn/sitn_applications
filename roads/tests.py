import json

from django.conf import settings
from django.contrib.gis.geos import GEOSGeometry, MultiLineString

from rest_framework.test import APITestCase

from roads.models import AxisSegment


class RoadsApiTest(APITestCase):

    def test_vmdeport_export_basic(self):
        """
        Extract linestring from a single segment and verify distances.
        Depart and finish are on the same AxisSegment:

        [38]----d-----[39]---f---[40]
        """

        f_dist_d = 705
        f_dist_f = 753

        # Line to extract
        url = (
            "/roads/vmdeport_export/?f_prop=NE&f_axe=H10&f_sens=="
            "&f_pr_d=38&f_pr_f=39"
            f"&f_dist_d={f_dist_d}&f_dist_f={f_dist_f}"
        )
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        wkt = json.loads(response.content)
        line = GEOSGeometry(wkt, srid=settings.DEFAULT_SRID)
        
        # Distance from point d to Sector 39
        url = (
            "/roads/vmdeport_export/?f_prop=NE&f_axe=H10&f_sens=="
            "&f_pr_d=38&f_pr_f=39"
            f"&f_dist_d={f_dist_d}&f_dist_f=0"
        )
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        wkt = json.loads(response.content)
        line_from_pr_d = GEOSGeometry(wkt, srid=settings.DEFAULT_SRID)

        # Distance from Sector 39 to point f
        url = (
            "/roads/vmdeport_export/?f_prop=NE&f_axe=H10&f_sens=="
            "&f_pr_d=39&f_pr_f=39"
            f"&f_dist_d=0&f_dist_f={f_dist_f}"
        )
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        wkt = json.loads(response.content)
        line_from_pr_f = GEOSGeometry(wkt, srid=settings.DEFAULT_SRID)
        self.assertAlmostEqual(
            line_from_pr_f.length,
            f_dist_f,
            places=3,
            msg="Extract from 0 to f_dist is equal to geometry length"
        )
        
        # Check sums of distances equals to overall extraction
        self.assertAlmostEqual(
            line_from_pr_d.length + line_from_pr_f.length,
            line.length,
            places=3,
            msg="Distances from 3 different extractions are matching"
        )

    def test_vmdeport_export_multi(self):
        """
        Extract multilinestring from a 3 segments
        
        [38]----d-----[39]-------[40]  [50]----[51]  [120]----f---[121]  [150]----[151]
        """
        url = (
            "/roads/vmdeport_export/?f_prop=NE&f_axe=H10&f_sens=="
            "&f_pr_d=38&f_pr_f=120&f_dist_d=20&f_dist_f=50"
        )
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        wkt = json.loads(response.content)
        multi_line = GEOSGeometry(wkt, srid=settings.DEFAULT_SRID)
        self.assertIsInstance(multi_line, MultiLineString, "Must be a MULTILINESTRING")
        self.assertEqual(multi_line.num_geom, 3, "Must have 3 parts")


    def test_vmdeport_export_whole(self):
        """
        This extracts the whole AxisSegment.
        Also, this particuliar AxisSegment doesn't have asg_sequence value.
        
         d            f
        [1]----------[2]
        """
        url = (
            "/roads/vmdeport_export/?f_prop=6458&f_axe=9048&f_sens=="
            "&f_pr_d=1&f_pr_f=2&f_dist_d=0.0&f_dist_f=0.0&f_ecart_d=0.0&f_ecart_f=0.0&f_usaneg=0.0"
        )
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        wkt = json.loads(response.content)
        line = GEOSGeometry(wkt, srid=settings.DEFAULT_SRID)
        
        segment = AxisSegment.objects.get(asg_name='6458:9048=:1')
        self.assertAlmostEqual(
            line.length,
            segment.asg_geom.length,
            "Extraction must have the same length as the original AxisSegment"
        )
