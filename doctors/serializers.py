from rest_framework import serializers
from doctors.models import St20AvailableDoctors


class St20AvailableDoctorsSerializer(serializers.ModelSerializer):
    class Meta:
        model = St20AvailableDoctors
        exclude = ['login_email']


class DoctorEmailSerializer(serializers.ModelSerializer):
    class Meta:
        model = St20AvailableDoctors
        fields = ['id_person_address', 'login_email']
