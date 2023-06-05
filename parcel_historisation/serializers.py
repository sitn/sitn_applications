from rest_framework import serializers
from parcel_historisation.models import Plan, Designation, State

class PlanSerializer(serializers.HyperlinkedModelSerializer):

    designation = serializers.SlugRelatedField(
        queryset=Designation.objects.all(),
        slug_field='filename')

    state = serializers.SlugRelatedField(
        queryset=State.objects.all(),
        slug_field='name')

   # Keeping that as an example (1)
   # roro = serializers.SerializerMethodField()

    class Meta:
        model = Plan
        fields = ['id', 'plan_number', 'designation', 'state', 'date_plan']

    # Keeping that as an example (2)
    # def get_roro(self, obj):
    #     result = None
    #     if obj.designation:
    #         result = obj.designation.name.split('/')[0]
    #     return result
