from django.conf import settings
from django.contrib.auth.decorators import permission_required
from django.http import FileResponse, HttpResponse, JsonResponse
from django.template import loader
from rest_framework import viewsets, filters
from rest_framework.decorators import api_view, parser_classes
from rest_framework.parsers import MultiPartParser, FormParser
from openpyxl import load_workbook

import json
import pathlib
import datetime
import os
import uuid

from parcel_historisation.models import Plan, Operation, OtherOperation, State, DivisonReunion, Balance
from parcel_historisation.serializers import PlanSerializer, BalanceSerializer


class PlanViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint that allows plans to be listed in read-only mode.
    """

    serializer_class = PlanSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["plan", "designation", "state", "date_plan"]

    ordering_fields = ["plan", "designation", "state", "date_plan"]
    ordering = ["date_plan"]

    def get_queryset(self):
        if self.request.query_params.get("numcad"):
            numcad = int(self.request.query_params.get("numcad"))
            queryset = Plan.objects.filter(cadastre=numcad).all()
        else:
            queryset = Plan.objects.all()

        return queryset


@permission_required("parcel_historisation.view_designation", raise_exception=True)
def index(request):
    """
    Serving the base template.
    """

    template = loader.get_template("parcel_historisation/index.html")

    context = {"infolica_api_url": settings.INTRANET_PROXY.get("infolica_api_url")}

    return HttpResponse(template.render(context, request))


@permission_required("parcel_historisation.view_designation", raise_exception=True)
def get_docs_list(request):
    """
    Gets the list of documents which have to be analysed, thus having a state
    equal to one. The list is generated regarding a specified cadastre
    """

    # TODO: parameter validation (try int(numcad) except BadRequest)
    numcad = request.GET["numcad"]

    results = Plan.objects.filter(state__id=1).filter(cadastre=int(numcad)).order_by("-date_plan", "link").all()

    load = []
    for result in results:
        load.append(
            {
                "link": result.link,
                "id": result.id,
                "designation_id": result.designation.id if result.designation else None,
            }
        )
    first = results[0]

    if first.designation is not None:
        download = first.designation.name
    else:
        download = first.name

    return JsonResponse({"list": load, "download": download}, safe=False)


@permission_required("parcel_historisation.view_designation", raise_exception=True)
def file_download(request, name):
    """
    Data download view

    The whole path to the file has to be passed in the URL
    """

    base_path = settings.NEARCH2_CONSULTATION

    path = pathlib.Path(base_path + "/Plans_de_mutations/" + name)

    return FileResponse(open(path, "rb"))


@permission_required("parcel_historisation.view_designation", raise_exception=True)
def get_download_path(request):
    """
    For a plan (or a designation -> depends on the type parameter),
    gets the whole download path (see file_download function)
    """

    id_ = request.GET["id"]
    type_ = request.GET["type"]

    object_ = Plan.objects.get(pk=id_)

    if type_ == "plan":
        download_path = object_.name
    elif type_ == "designation":
        download_path = object_.designation.name

    return JsonResponse({"download_path": download_path}, safe=False)


@permission_required("parcel_historisation.view_designation", raise_exception=True)
def submit_saisie(request):
    """
    Process data submitted by user in the base form
    """

    data = json.loads(request.body)
    has_div = False
    plan = Plan.objects.get(pk=data["id"])

    if data["delayed_check"] is True:
        state = State.objects.get(pk=3)
        plan.state = state
        plan.save()
        return JsonResponse({"submitted": False, "has_div": has_div}, safe=False)

    now = datetime.datetime.now()
    op = Operation(date=now, user=request.META["HTTP_REMOTE_USER"], complement=data["complement"], plan=plan)

    op.save()

    if data["div_check"] is True:
        div = DivisonReunion(operation=op)
        div.save()
        has_div = True

    if data["cad_check"] is True:
        other = OtherOperation(operation=op, type=1)
        other.save()

    if data["serv_check"] is True:
        other = OtherOperation(operation=op, type=2)
        other.save()

    if data["art35_check"] is True:
        other = OtherOperation(operation=op, type=3)
        other.save()

    if data["other_check"] is True:
        other = OtherOperation(operation=op, type=4)
        other.save()

    if data["cad_check"] is True:
        state = State.objects.get(pk=4)
    else:
        state = State.objects.get(pk=2)

    plan.state = state
    plan.save()

    return JsonResponse(
        {
            "submitted": True,
            "has_div": has_div,
            "operation_id": op.id,
        }
    )


class BalanceViewSet(viewsets.ViewSet):
    """
    API endpoint to handle balances.
    """

    serializer_class = BalanceSerializer
    queryset = Balance.objects.all()

    # def retrieve(self, request, division_pk=None):
    #     queryset = Balance.objects.filter(division__pk=division_pk)
    #     balance = get_object_or_404(queryset, pk=pk)
    #     serializer = UserSerializer(user)
    #     return Response(serializer.data)

    #     return queryset

    # def


@permission_required("parcel_historisation.view_designation", raise_exception=True)
def submit_balance(request):
    """
    save balance
    """

    data = json.loads(request.body)

    # save balance
    if data["balance"] is not None:
        for relation in data["balance"]:
            balance = Balance()
            rel = relation.split("-")

            # control if dp is in old/new parcel of relation
            for i, parcel in enumerate(rel):
                if "dp" in parcel.lower():
                    rel[i] = "DP"

            # check that parcel relation does not already exist
            checkRel = Balance.objects.filter(source=rel[0], destination=rel[1], division_id=data["division_id"]).first()
            if checkRel is not None:
                continue

            balance.source = rel[0]
            balance.destination = rel[1]
            balance.division_id = data["division_id"]

            balance.save()

    # save ddp relations
    if data["ddp"] is not None:
        for relation in data["ddp"]:
            balance = Balance()
            rel = relation.split("-")

            # check that parcel relation does not already exist
            checkRel = Balance.objects.filter(source=rel[0], destination=rel[1], division_id=data["division_id"]).first()
            if checkRel is not None:
                continue

            balance.source = rel[0]
            balance.destination = rel[1]
            balance.is_ddp = True
            balance.division_id = data["division_id"]

            balance.save()

    return JsonResponse(
        {
            "submitted": True,
        }
    )


@permission_required("parcel_historisation.view_designation", raise_exception=True)
@api_view(["POST"])
@parser_classes([MultiPartParser, FormParser])
def balance_file_upload(request):
    """
    Upload balance file
    """
    cadnum = request.POST.get("cadnum")
    file = request.FILES.get("file")

    filepath = pathlib.Path("C:\\Users\\rufenerm\\Desktop\\test\\" + f"{file.name}_{uuid.uuid4()}.xlsx")

    # save temporary_file
    with open(filepath, "wb+") as f:
        for chunk in file.chunks():
            f.write(chunk)

    # do stuff
    wb = load_workbook(filepath)
    ws = wb.active

    # get old parcels
    new_bf = []
    i = 1
    while ws.cell(1, i + 2).value is not None:
        new_bf.append(ws.cell(1, i + 2).value)
        i += 1
    new_bf = list(set(new_bf))
    if "dp" in new_bf:
        new_bf.remove("dp")
        new_bf.sort()
        new_bf.append("dp")
    else:
        new_bf.sort()

    # get old parcels
    old_bf = []
    i = 1
    while ws.cell(i + 1, 2).value is not None:
        old_bf.append(ws.cell(i + 1, 2).value)
        i += 1
    old_bf = list(set(old_bf))
    if "dp" in old_bf:
        old_bf.remove("dp")
        old_bf.sort()
        old_bf.append("dp")
    else:
        old_bf.sort()

    relations = []
    for row_id in range(len(old_bf)):
        for col_id in range(len(new_bf)):
            if ws.cell(row_id + 2, col_id + 3).value is not None:
                relations.append([ws.cell(row_id + 2, 2).value, ws.cell(1, col_id + 3).value])

    # print('relations:', relations)

    balance = None
    if len(old_bf) > 0 and len(new_bf) > 0:
        # initialize balance 2d list
        balance = [[" " for j in range(len(new_bf) + 1)] for i in range(len(old_bf) + 1)]

        # 1rst line and row for headers
        for i in range(len(old_bf)):
            tmp = str(old_bf[i])
            if not str(old_bf[i]) == "dp":
                tmp = "_".join([str(cadnum), str(old_bf[i])])
            balance[i + 1][0] = tmp

        for j in range(len(new_bf)):
            tmp = str(new_bf[j])
            if not str(new_bf[j]) == "dp":
                tmp = "_".join([str(cadnum), str(new_bf[j])])
            balance[0][j + 1] = tmp

        for rel in relations:
            src_idx = old_bf.index(rel[0]) + 1
            dst_idx = new_bf.index(rel[1]) + 1
            balance[src_idx][dst_idx] = "X"

    # remove temporary_file
    os.remove(filepath)

    return JsonResponse({"balance": balance})
