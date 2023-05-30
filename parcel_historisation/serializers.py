from rest_framework import serializers
from parcel_historisation.models import Plan, Designation

class DesignationSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Designation
        fields = ['name']

class PlanSerializer(serializers.HyperlinkedModelSerializer):

    designation = serializers.SlugRelatedField(
        queryset=Designation.objects.all(),
        slug_field='filename')
  
    roro = serializers.SerializerMethodField()

    class Meta:
        model = Plan
        fields = ['plan_number', 'link', 'designation', 'roro', 'date_plan']

    def get_roro(self, obj):
        result = None
        if obj.designation:
            result = obj.designation.name.split('/')[0]

        return result
