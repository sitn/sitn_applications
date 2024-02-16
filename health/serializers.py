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


class DoctorEmailSerializer(serializers.Serializer):
    id_person_address = serializers.CharField()
    login_email = serializers.EmailField()


class DoctorUUIDSerializer(St20AvailableDoctorsSerializer):
    """
    This serializer protects edit_guid from beeing retrieved
    On update, it will set edit_guid to None not allowing an edit anymore until a new guid is requested
    """
    edit_guid = serializers.SerializerMethodField()

    @classmethod
    def get_edit_guid(self, obj):
        return ''

    class Meta(St20AvailableDoctorsSerializer.Meta):
        fields = St20AvailableDoctorsSerializer.Meta.fields + ['edit_guid']
        read_only_fields = ['id_person_address', 'edit_guid']

    def update(self, instance, validated_data):
        instance.edit_guid = None
        return super().update(instance, validated_data)
