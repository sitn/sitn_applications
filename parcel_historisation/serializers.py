from rest_framework import serializers
from parcel_historisation.models import Plan, Designation, State, Operation, Balance, DivisonReunion


class PlanSerializer(serializers.ModelSerializer):

    operation_id = serializers.SerializerMethodField()

    designation = serializers.SlugRelatedField(
        queryset=Designation.objects.all(),
        slug_field="filename")

    state = serializers.SlugRelatedField(
        queryset=State.objects.all(),
        slug_field="name")

    class Meta:
        model = Plan
        fields = ["id", "plan_number", "designation", "state", "date_plan", "operation_id"]

    def get_operation_id(self, obj):
        op = Operation.objects.filter(plan=obj.id).first()
        return op.id if op is not None else None


class OperationSerializer(serializers.ModelSerializer):

    plan_link = serializers.SerializerMethodField()
    plan_name = serializers.SerializerMethodField()
    designation_name = serializers.SerializerMethodField()
    designation_id = serializers.SerializerMethodField()
    cadastre_id = serializers.SerializerMethodField()
    operation_types = serializers.SerializerMethodField()
    plan_retarde = serializers.SerializerMethodField()

    class Meta:
        model = Operation
        fields = ["id", "complement", "infolica_no", "plan", "plan_link", "plan_name", "designation_name", "plan_id", "designation_id", "cadastre_id", "operation_types", "plan_retarde"]

    def get_plan_link(self, obj):
        return obj.plan.link

    def get_plan_name(self, obj):
        return obj.plan.name

    def get_designation_name(self, obj):
        des = Designation.objects.filter(id=obj.plan.designation_id).first()
        return des.name if des is not None else None

    def get_designation_id(self, obj):
        return obj.plan.designation_id

    def get_cadastre_id(self, obj):
        return obj.plan.cadastre

    def get_operation_types(self, obj):
        types = {}
        other = [op.type for op in obj.operations.all()]

        types["cad_check"] = True if 1 in other else False
        types["serv_check"] = True if 2 in other else False
        types["art35_check"] = True if 3 in other else False
        types["other_check"] = True if 4 in other else False

        div_test = DivisonReunion.objects.filter(operation_id=obj.id).exists()
        types["div_check"] = True if div_test is True else False

        return types

    def get_plan_retarde(self, obj):
        return True if obj.plan.state.id == 3 else False


class BalanceSerializer(serializers.ModelSerializer):

    class Meta:
        model = Balance
        fields = "__all__"
