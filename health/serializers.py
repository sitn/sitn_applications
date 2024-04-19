from django.utils import timezone
from rest_framework import serializers
from health.models import St20AvailableDoctors, St21AvailableDoctorsWithGeom, St22DoctorChangeSuggestion


class St20AvailableDoctorsSerializer(serializers.HyperlinkedModelSerializer):
    id_person_address = serializers.SerializerMethodField()
    email1 = serializers.EmailField(write_only=True, required=False)
    email2 = serializers.EmailField(write_only=True, required=False)
    class Meta:
        model = St20AvailableDoctors
        fields = [
            'url',
            'id_person_address',
            'email1',
            'email2',
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
    
    def validate(self, data):
        validated_data = super().validate(data)
        if 'email1' in validated_data.keys():
            if validated_data['email1'] != data['email2']:
                raise serializers.ValidationError("The two email fields didn't match.")
        return validated_data

    def update(self, instance, validated_data):
        if 'email1' in validated_data.keys():
            validated_data.pop('email2')
            instance.login_email = validated_data.pop('email1')
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
