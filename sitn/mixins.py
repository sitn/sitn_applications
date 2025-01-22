from django.db.models import Value, F, JSONField
from django.db.models.functions import Cast
from django.contrib.gis.db.models.functions import AsGeoJSON
from django.contrib.postgres.aggregates import JSONBAgg
from sitn.functions import JsonBuildObject


class GeoJSONModelMixin:
    """
    A mixin to add database GeoJSON serialization to a GeoDjango model.
    Usefull to get the list of all features with good performance.

    You must define PUBLIC_FIELDS: a list of fields that will be serialized into GeoJSON
    as properties.
    """

    @classmethod
    def as_geojson(cls):
        """
        Generate a GeoJSON representation of the model's including all its PUBLIC_FIELDS as properties
        """
        if not hasattr(cls, "PUBLIC_FIELDS"):
            raise AttributeError(
                f"{cls.__name__} must define a PUBLIC_FIELDS attribute."
            )

        if not hasattr(cls, "geom"):
            raise AttributeError(
                f"{cls.__name__} must define a 'geom' attribute as geometric field."
            )

        properties_fields = []

        for field in cls.PUBLIC_FIELDS:
            if field != "geom":
                properties_fields.extend([Value(field), F(field)])

        geojson_data = cls.objects.aggregate(
            geojson=Cast(
                JsonBuildObject(
                    Value("type"),
                    Value("FeatureCollection"),
                    Value("features"),
                    JSONBAgg(
                        JsonBuildObject(
                            Value("type"), Value("Feature"),
                            Value("geometry"), Cast(AsGeoJSON("geom"), output_field=JSONField()),
                            Value("properties"), JsonBuildObject(*properties_fields),
                        )
                    ),
                ),
                output_field=JSONField(),
            )
        )
        return geojson_data['geojson']
