from django.db.models import Func, JSONField
from django.contrib.gis.db.models import MultiLineStringField, LineStringField, PointField


class JsonBuildObject(Func):
    function = 'json_build_object'
    output_field = JSONField()


class LineSubstring(Func):
    function = "ST_LineSubstring"
    output_field = LineStringField()


class LineMerge(Func):
    function = "ST_LineMerge"
    output_field = MultiLineStringField()


class OffsetCurve(Func):
    function = "ST_OffsetCurve"
    output_field = MultiLineStringField()


class LineInterpolatePoint(Func):
    function = "ST_LineInterpolatePoint"
    output_field = PointField()
