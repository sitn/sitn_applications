from rest_framework import serializers
from parcel_historisation.models import Plan, Designation, State, Balance

class PlanSerializer(serializers.HyperlinkedModelSerializer):

    designation = serializers.SlugRelatedField(
        queryset=Designation.objects.all(),
        slug_field='filename')

    state = serializers.SlugRelatedField(
        queryset=State.objects.all(),
        slug_field='name')

    class Meta:
        model = Plan
        fields = ['id', 'plan_number', 'designation', 'state', 'date_plan']


class BalanceSerializer(serializers.HyperlinkedModelSerializer):

    class Meta:
        model = Balance
        fields = "__all__"
