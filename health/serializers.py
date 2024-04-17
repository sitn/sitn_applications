from django.utils import timezone
from rest_framework import serializers
from health.models import St20AvailableDoctors, St21AvailableDoctorsWithGeom, St22DoctorChangeSuggestion


class St20AvailableDoctorsSerializer(serializers.HyperlinkedModelSerializer):
    id_person_address = serializers.SerializerMethodField()
    class Meta:
        model = St20AvailableDoctors
        fields = [
            'url',
            'id_person_address',
            'availability_conditions',
            'public_phone',
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
    has_parking = serializers.BooleanField()
    has_disabled_access = serializers.BooleanField()
    has_lift = serializers.BooleanField()
    is_rsn_member = serializers.BooleanField()
    class Meta:
        model = St21AvailableDoctorsWithGeom
        fields = St21AvailableDoctorsWithGeom.PUBLIC_FIELDS


class St22DoctorChangeSuggestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = St22DoctorChangeSuggestion
        fields = [
            'doctor', 'availability', 'comments'
        ]
