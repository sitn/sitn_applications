from rest_framework import serializers


class VmDeportExportSerializer(serializers.Serializer):
    f_prop = serializers.CharField(max_length=12, label="Owner of the axis (ie. NE)")
    f_axe = serializers.CharField(max_length=64, label="Name of the axis (ie. 1161)")
    f_sens = serializers.ChoiceField(choices=["+", "-", "="], label="Direction of the axis (ie. =)")
    f_pr_d = serializers.CharField(max_length=64, label="Starting sector or departure (ie. 5)")
    f_pr_f = serializers.CharField(max_length=64, label="Ending sector or finish (ie. 7)")
    f_dist_d = serializers.FloatField(min_value=0.0, label="Distance from starting sector (ie. 200.0)")
    f_dist_f = serializers.FloatField(min_value=0.0, label="Distance from starting sector (ie. 300.0)")

    f_ecart_d = serializers.FloatField(required=False, default=0.0, label="Offset at the starting point perpendicular from line (ie. 0)")
    f_ecart_f = serializers.FloatField(required=False, default=0.0, label="Offset at the ending point perpendicular from line (ie. 0)")
    f_usaneg = serializers.FloatField(required=False, default=0.0, label="Offset at the ending point perpendicular from line (ie. 0)")

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