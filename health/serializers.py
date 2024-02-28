from django.utils import timezone
from rest_framework import serializers
from health.models import St20AvailableDoctors


class St20AvailableDoctorsSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = St20AvailableDoctors
        fields = [
            'url',
            'id_person_address',
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
