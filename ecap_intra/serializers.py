from rest_framework_gis.serializers import GeoFeatureModelSerializer
from rest_framework.serializers import HyperlinkedModelSerializer

from ecap_intra.models import ObjetImmobilise, RepartitionExpert, PlanQuartier, PlanSpecial


class ObjetImmobiliseSerializer(GeoFeatureModelSerializer):
    class Meta:
        model = ObjetImmobilise
        geo_field = 'geom'
        fields = ObjetImmobilise.PUBLIC_FIELDS + ['url']


class RepartitionExpertDigestSerializer(HyperlinkedModelSerializer):
    class Meta:
        model = RepartitionExpert
        fields = RepartitionExpert.PUBLIC_FIELDS + ['url']


class RepartitionExpertSerializer(GeoFeatureModelSerializer):
    class Meta:
        model = RepartitionExpert
        geo_field = 'geom'
        fields = RepartitionExpert.PUBLIC_FIELDS + ['url']


class PlanQuartierSerializer(GeoFeatureModelSerializer):
    class Meta:
        model = PlanQuartier
        geo_field = 'geom'
        fields = PlanQuartier.PUBLIC_FIELDS + ['url']


class PlanSpecialSerializer(GeoFeatureModelSerializer):
    class Meta:
        model = PlanSpecial
        geo_field = 'geom'
        fields = PlanSpecial.PUBLIC_FIELDS + ['url']
