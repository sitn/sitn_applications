from rest_framework_gis import serializers
from ecap_intra.models import ObjetImmobilise

class ObjetImmobiliseSerializer(serializers.GeoFeatureModelSerializer):
    class Meta:
        model = ObjetImmobilise
        geo_field = 'geom'
        fields = ['no_obj']
