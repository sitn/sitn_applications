from rest_framework import serializers
from .models import AxisSegment, Sector


class AxisSegmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = AxisSegment
        fields = ["asg_name"]


class SectorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Sector
        fields = ["sec_name", "sec_length", "sec_km"]


class VmDeportExportSerializer(serializers.Serializer):
    f_prop = serializers.CharField(max_length=12)
    f_axe = serializers.CharField(max_length=64)
    f_sens = serializers.ChoiceField(choices=["+", "-", "="])
    f_pr_d = serializers.CharField(max_length=64)
    f_pr_f = serializers.CharField(max_length=64)
    f_dist_d = serializers.FloatField(min_value=0.0)
    f_dist_f = serializers.FloatField(min_value=0.0)

    f_ecart_d = serializers.FloatField(required=False, default=0.0)
    f_ecart_f = serializers.FloatField(required=False, default=0.0)
    f_usaneg = serializers.BooleanField(required=False, default=False)

    def validate(self, data):
        if data["f_ecart_d"] != data["f_ecart_f"]:
            raise serializers.ValidationError(
                "Le calcul d'un déport biais n'est pas encore implémenté."
            )
        return data
    
    def validate_f_prop(self, value):
        return value.strip().upper()

    def validate_f_axe(self, value):
        return value.strip().upper()

    def validate_f_pr_d(self, value):
        return value.strip().upper()

    def validate_f_pr_f(self, value):
        return value.strip().upper()