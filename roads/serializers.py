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
