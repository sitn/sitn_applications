from rest_framework import serializers
from health.models import St20AvailableDoctors


class St20AvailableDoctorsSerializer(serializers.ModelSerializer):
    class Meta:
        model = St20AvailableDoctors
        fields = [
            'id_person_address',
            'spoken_languages',
            'availability',
            'availability_conditions'
        ]


class DoctorEmailSerializer(serializers.ModelSerializer):
    class Meta:
        model = St20AvailableDoctors
        fields = ['id_person_address', 'login_email']
        read_only_fields = ['id_person_address', 'login_email']
