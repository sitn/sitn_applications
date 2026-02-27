import json

from django.conf import settings
from django.contrib.gis.geos import GEOSGeometry, MultiLineString, Point

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
            749.634,
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

    def test_vmdeport_export_whole_segment(self):
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
            places=3,
            msg="Extraction must have the same length as the original AxisSegment"
        )

    def test_vmdeport_export_too_long(self):
        """
        If the distance from Sector is too long, the resulting line will be truncated 
        to the length of the axis segment.
        
         d                f
        [1]----------[2]
        """
        url = (
            "/roads/vmdeport_export/?f_prop=NE&f_axe=1162&f_sens=="
            "&f_pr_d=0&f_pr_f=8&f_dist_d=0.0&f_dist_f=676.2"
        )
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        wkt = json.loads(response.content)
        line = GEOSGeometry(wkt, srid=settings.DEFAULT_SRID)
        
        segment = AxisSegment.objects.get(asg_name='NE:1162=:0')
        self.assertAlmostEqual(
            line.length,
            segment.asg_geom.length,
            places=3,
            msg="Extraction must have the same length as the original AxisSegment"
        )

    def test_vmdeport_export_unknown_axis(self):
        """
        An unknown axis should return a 400.
        """
        url = (
            "/roads/vmdeport_export/?f_prop=6401&f_axe=500&f_sens=="
            "&f_pr_d=0&f_pr_f=8&f_dist_d=0.0&f_dist_f=676.2"
        )
        response = self.client.get(url)
        self.assertEqual(response.status_code, 400)

    def test_vmdeport_export_point(self):
        """
        When depart and finish are the same, we want a Point.
         
        """
        url = (
            "/roads/vmdeport_export/?f_prop=6458&f_axe=642&f_sens=%3D"
            "&f_pr_d=1&f_pr_f=1&f_dist_d=23.0&f_dist_f=23.0&f_ecart_d=-1.0&f_ecart_f=-1.0"
        )
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        wkt = json.loads(response.content)
        point = GEOSGeometry(wkt, srid=settings.DEFAULT_SRID)
        self.assertIsInstance(point, Point, "Must be a POINT")

    def test_axis_list(self):
        """
        /roads/axissegments/ returns a list of axis objects
        Used in MACADAM
        """
        
        url = "/roads/axissegments/"
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIsInstance(data, list)
        if data:
            self.assertIn("asg_iliid", data[0])
            self.assertIn("asg_name", data[0])
            self.assertIn("sectors", data[0])

    def test_axis_filter(self):
        """
        /roads/axissegments/?search=... filters axis by asg_name
        """
        url = "/roads/axissegments/?search=H10"
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        for axis in data:
            self.assertIn("H10", axis["asg_name"])
            
    def test_sectors_list(self):
        """
        /roads/axissegments/<asg_iliid>/sectors/ returns sectors for axis
        """
        # Get an axis iliid from the list
        axis_url = "/roads/axissegments/"
        axis_response = self.client.get(axis_url)
        self.assertEqual(axis_response.status_code, 200)
        axis_data = axis_response.json()
        if axis_data:
            asg_iliid = axis_data[0]["asg_iliid"]
            url = f"/roads/axissegments/{asg_iliid}/sectors/"
            response = self.client.get(url)
            self.assertEqual(response.status_code, 200)
            sectors = response.json()["results"]
            self.assertIsInstance(sectors, list)
            for sector in sectors:
                self.assertIn("sec_name", sector)
                self.assertIn("sec_length", sector)
                self.assertIn("sec_km", sector)