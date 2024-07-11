from django.utils import timezone
from rest_framework import serializers
from health.models import (
    St20AvailableDoctors,
    St21AvailableDoctorsWithGeom,
    St22DoctorChangeSuggestion,
    St23HealthSite
)


class St20AvailableDoctorsSerializer(serializers.HyperlinkedModelSerializer):
    id_person_address = serializers.SerializerMethodField()
    class Meta:
        model = St20AvailableDoctors
        fields = [
            'url',
            'id_person_address',
            'availability_conditions',
            'public_phone',
            'public_first_name',
            'has_parking',
            'has_disabled_access',
            'has_lift',
            'spoken_languages',
            'is_rsn_member',
            'availability'
        ]
        read_only_fields = [
            'url',
            'id_person_address',
        ]

    def get_id_person_address(self, obj):
        return obj.pk

    def update(self, instance, validated_data):
        instance.edit_guid = None
        instance.guid_requested_when = None
        instance.last_edit = timezone.now()
        instance = super().update(instance, validated_data)
        return instance


class DoctorEmailSerializer(serializers.Serializer):
    login_email = serializers.EmailField()


class St21AvailableDoctorsWithGeomSerializer(serializers.ModelSerializer):
    class Meta:
        model = St21AvailableDoctorsWithGeom
        fields = St21AvailableDoctorsWithGeom.PUBLIC_FIELDS


class St22DoctorChangeSuggestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = St22DoctorChangeSuggestion
        fields = [
            'doctor', 'availability', 'comments'
        ]


class St23HealthSiteSerializer(serializers.ModelSerializer):
    class Meta:
        model = St23HealthSite
        fields = [
            'site_name', 'address', 'public_link'
        ]
