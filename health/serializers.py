from django.utils import timezone
from rest_framework import serializers
from health.models import St20AvailableDoctors, St21AvailableDoctorsWithGeom


class St20AvailableDoctorsSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = St20AvailableDoctors
        fields = [
            'url',
            'id_person_address',
            'nom',
            'prenoms',
            'spoken_languages',
            'availability',
            'availability_conditions'
        ]
        read_only_fields = [
            'url',
            'id_person_address',
        ]

    def update(self, instance, validated_data):
        instance.edit_guid = None
        instance.last_edit = timezone.now()
        instance = super().update(instance, validated_data)
        return instance


class DoctorEmailSerializer(serializers.Serializer):
    login_email = serializers.EmailField()


class St21AvailableDoctorsWithGeomSerializer(serializers.ModelSerializer):
    has_parking = serializers.BooleanField()
    has_disabled_access = serializers.BooleanField()
    has_lift = serializers.BooleanField()
    is_rsn_member = serializers.BooleanField()
    class Meta:
        model = St21AvailableDoctorsWithGeom
        fields = St21AvailableDoctorsWithGeom.PUBLIC_FIELDS
