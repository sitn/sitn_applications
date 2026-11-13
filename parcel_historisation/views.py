from django.conf import settings
from django.contrib.auth.decorators import permission_required
from django.forms.models import model_to_dict
from django.core.exceptions import PermissionDenied
from django.http import FileResponse, HttpResponse, JsonResponse
from django.template import loader
from rest_framework import viewsets, filters
from rest_framework.decorators import api_view, parser_classes
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.response import Response
from openpyxl import Workbook, load_workbook
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.utils import get_column_letter
from io import BytesIO

import json
import pathlib
import datetime

from parcel_historisation.models import Plan, Operation, OtherOperation, State, DivisonReunion, Balance
from parcel_historisation.models import VBalanceSourceNoDest, VBalanceDestNoSource
from parcel_historisation.serializers import PlanSerializer, OperationSerializer, BalanceSerializer


class PlanViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint that allows plans to be listed in read-only mode.
    """

    serializer_class = PlanSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["plan_number", "designation__name", "state__name", "date_plan"]

    ordering_fields = ["plan_number", "designation__name", "state__name", "date_plan"]
    ordering = ["date_plan"]

    def get_queryset(self):
        queryset = Plan.objects.all()

        numcad = self.request.query_params.get("numcad")

        if numcad:
            queryset = queryset.filter(cadastre=numcad)

        return queryset


def index(request):
    """
    Serving the base template.
    """

    template = loader.get_template("parcel_historisation/index.html")

    if not request.user.is_authenticated:
        return HttpResponse(template.render({}, request))

    if not request.user.has_perm("parcel_historisation.view_designation"):
        raise PermissionDenied

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

    results = Plan.objects.filter(state__id=1).filter(cadastre=int(numcad)).order_by("-plan_number", "index", "-scale").all()

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
def search_plans_by_term(request):
    """
    Gets the list of documents which have to be analysed, thus having a state
    equal to one. The list is generated regarding a specified cadastre
    """

    # TODO: parameter validation (try int(numcad) except BadRequest)
    data = json.loads(request.body)
    numcad = data["numcad"]
    searchterm = data["searchterm"]

    results = Plan.objects.filter(cadastre=int(numcad)).filter(link__startswith=searchterm).order_by("-plan_number", "index", "-scale").all()

    load = []
    for i, result in enumerate(results):

        if i >= 10:
            break

        load.append(
            result.link,
        )

    return JsonResponse(load, safe=False)


@permission_required("parcel_historisation.view_designation", raise_exception=True)
def file_download(request, name):
    """
    Data download view

    The whole path to the file has to be passed in the URL
    """

    base_path = settings.ARCHIVES_PATH

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
    op = Operation(date=now, user=request.user.username.split('@')[0].lower(), complement=data["complement"], plan=plan)

    operation_id = data["operation_id"] if "operation_id" in data else None
    if operation_id is not None:
        op.id = operation_id
    op.save()

    if data["div_check"] is True:
        div = DivisonReunion(operation=op)
        if not DivisonReunion.objects.filter(operation=div.operation).exists():
            div.save()
        has_div = True
    else:
        divs = DivisonReunion.objects.filter(operation=op).all()
        if len(divs) > 0:
            for div in divs:
                bal = Balance.objects.filter(division=div.id).all()  ## !! Cannot use QuerySet for "DivisonReunion": Use a QuerySet for "Operation"

                # remove balance if exists
                for tmp in bal:
                    tmp.delete()

                # remove division
                for tmp in div:
                    tmp.delete()

    # delete all other operations to update with incoming request
    op_type = OtherOperation.objects.filter(operation=op).all()
    for tmp in op_type:
        tmp.delete()


    if data["cad_check"] is True:
        other = OtherOperation(operation=op, type=1)
        if not OtherOperation.objects.filter(operation=other.operation, type=other.type).exists():
            other.save()

    if data["serv_check"] is True:
        other = OtherOperation(operation=op, type=2)
        if not OtherOperation.objects.filter(operation=other.operation, type=other.type).exists():
            other.save()

    if data["art35_check"] is True:
        other = OtherOperation(operation=op, type=3)
        if not OtherOperation.objects.filter(operation=other.operation, type=other.type).exists():
            other.save()

    if data["other_check"] is True:
        other = OtherOperation(operation=op, type=4)
        if not OtherOperation.objects.filter(operation=other.operation, type=other.type).exists():
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
            "plan_link": plan.link,
        }
    )


def _build_balance(relations):
    source_bf = []
    destination_bf = []
    relations_ = []

    for rel in relations:
        if rel["destination"]:
            source_bf.append(rel["source"]) if not rel["source"] in source_bf else None
            destination_bf.append(rel["destination"]) if not rel["destination"] in destination_bf else None
            relations_.append([rel["source"], rel["destination"]])

    # rename "0_1" into "DP" and rename "0_2" into "RP"
    source_bf = ["DP" if x == "0_1" else x for x in source_bf]
    destination_bf = ["DP" if x == "0_1" else x for x in destination_bf]
    relations_ = [["DP" if y == "0_1" else y for y in x] for x in relations_]
    source_bf = ["RP" if x == "0_2" else x for x in source_bf]
    destination_bf = ["RP" if x == "0_2" else x for x in destination_bf]
    relations_ = [["RP" if y == "0_2" else y for y in x] for x in relations_]

    source_bf.sort()
    destination_bf.sort()

    balance = None

    if len(source_bf) > 0 and len(destination_bf) > 0:
        # initialize balance 2d list
        balance = [[" " for j in range(len(destination_bf) + 1)] for i in range(len(source_bf) + 1)]

        # 1rst line and row for headers
        for i in range(len(source_bf)):
            balance[i + 1][0] = source_bf[i]

        for j in range(len(destination_bf)):
            balance[0][j + 1] = destination_bf[j]

        for rel in relations_:
            src_idx = source_bf.index(rel[0]) + 1
            dst_idx = destination_bf.index(rel[1]) + 1
            balance[src_idx][dst_idx] = "X"

    return balance


class BalanceViewSet(viewsets.ViewSet):
    """
    API endpoint to handle balances.
    """

    queryset = Balance.objects.all()
    serializer_class = BalanceSerializer

    def retrieve(self, request, pk):
        instances = Balance.objects.filter(division=pk)
        relations = {}
        relations["balance"] = []
        relations["ddp"] = []
        for rel in instances:
            if rel.immatriculation_ddp or rel.exmatriculation_ddp:
                relations["ddp"].append(
                    {
                        "relation": "-".join([rel.source, rel.destination]),
                        "immatriculation": rel.immatriculation_ddp,
                    }
                )
            else:
                relations["balance"].append({"source": rel.source, "destination": rel.destination})

        # Sort results
        relations["balance"] = _build_balance(relations["balance"])
        relations["ddp"] = sorted(
            relations["ddp"],
            key=lambda item: (
                int(item["relation"].split("-")[1].split("_")[0]),
                int(item["relation"].split("-")[1].split("_")[1]),
                int(item["relation"].split("_")[0]),
                int(item["relation"].split("_")[1].split("-")[0]),
            ),
        )

        return Response(relations)


@permission_required("parcel_historisation.view_designation", raise_exception=True)
def submit_balance(request):
    """
    save balance
    """

    data = json.loads(request.body)

    # remove existing relations and (re-)create them
    data2remove = Balance.objects.filter(division_id=data["division_id"]).all()
    for _ in data2remove:
        _.delete()

    # save balance
    if data["balance"] is not None:
        for relation in data["balance"]:
            balance = Balance()
            rel = relation.split("-")

            # control if dp is in old/new parcel of relation
            for i, parcel in enumerate(rel):
                if "dp" in parcel.lower():
                    rel[i] = "DP"

            balance.source = rel[0]
            balance.destination = rel[1]
            balance.division_id = data["division_id"]

            balance.save()

    # save ddp relations
    if data["ddp"] is not None:
        for item in data["ddp"]:
            balance = Balance()
            rel = item["relation"].split("-")
            immatriculation = bool(item["immatriculation"])

            balance.source = rel[0]
            balance.destination = rel[1]
            balance.immatriculation_ddp = immatriculation
            balance.exmatriculation_ddp = not immatriculation
            balance.division_id = data["division_id"]

            balance.save()

    return JsonResponse(
        {
            "submitted": True,
        }
    )


@permission_required("parcel_historisation.view_designation", raise_exception=True)
def export_balance_excel(request):
    """
    Export the balance displayed in the frontend (and its DDP) to an Excel file,
    keeping the layout of the HTML table.
    """
    if request.method != "POST":
        return HttpResponse(status=405)

    data = json.loads(request.body)
    balance = data.get("balance") or []
    ddp = data.get("ddp") or []

    thin = Side(style="thin", color="000000")
    border = Border(left=thin, right=thin, top=thin, bottom=thin)
    bold = Font(bold=True)

    wb = Workbook()

    # Balance sheet: old parcels in rows, new parcels in columns
    ws = wb.active
    ws.title = "Balance"
    for i, row in enumerate(balance):
        for j, value in enumerate(row):
            cell = ws.cell(row=i + 1, column=j + 1, value=value or None)
            if i == 0 and j == 0:
                continue
            cell.border = border
            if i == 0:
                # new parcels: vertical text, like the rotated header in the frontend
                cell.alignment = Alignment(horizontal="center", vertical="bottom", text_rotation=90)
                cell.font = bold
            elif j == 0:
                cell.alignment = Alignment(horizontal="right", vertical="center")
                cell.font = bold
            else:
                cell.alignment = Alignment(horizontal="center", vertical="center")

    if balance:
        ws.column_dimensions["A"].width = max(len(str(row[0] or "")) for row in balance) + 4
        for j in range(1, len(balance[0])):
            ws.column_dimensions[get_column_letter(j + 1)].width = 5
        header_length = max(len(str(value or "")) for value in balance[0])
        ws.row_dimensions[1].height = max(15, header_length * 7)
        ws.freeze_panes = "B2"

    # DDP sheet, colored like the badges in the frontend
    if ddp:
        ws_ddp = wb.create_sheet("DDP")
        headers = ["Statut", "DDP", "Bien-fonds de base"]
        for j, header in enumerate(headers):
            cell = ws_ddp.cell(row=1, column=j + 1, value=header)
            cell.font = bold
            cell.border = border
        fills = {
            True: PatternFill(fill_type="solid", start_color="0D6EFD", end_color="0D6EFD"),
            False: PatternFill(fill_type="solid", start_color="DC3545", end_color="DC3545"),
        }
        for i, item in enumerate(ddp):
            base, ddp_number = item["relation"].split("-")
            immatriculation = bool(item["immatriculation"])
            values = ["Immatriculation" if immatriculation else "Exmatriculation", ddp_number, base]
            for j, value in enumerate(values):
                cell = ws_ddp.cell(row=i + 2, column=j + 1, value=value)
                cell.border = border
                cell.fill = fills[immatriculation]
                cell.font = Font(color="FFFFFF", bold=(j == 1))
        for column, width in zip("ABC", (18, 15, 20)):
            ws_ddp.column_dimensions[column].width = width

    output = BytesIO()
    wb.save(output)
    output.seek(0)

    filename = f"balance_{data.get('operation_id') or 'export'}.xlsx"
    response = HttpResponse(
        output.getvalue(),
        content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )
    response["Content-Disposition"] = f'attachment; filename="{filename}"'
    return response


@permission_required("parcel_historisation.view_designation", raise_exception=True)
@api_view(["POST"])
@parser_classes([MultiPartParser, FormParser])
def balance_file_upload(request):
    """
    Upload balance file
    """
    file = request.FILES.get("file")
    if file is None:
        return JsonResponse({"error": "Aucun fichier n'a été transmis."}, status=400)

    # Only the following format is accepted:
    # - sheet "Balance": old parcels in column A from row 2, new parcels in row 1 from column B,
    #   cells with a value = relation, labels "<cadastre>_<number>", "DP" or "RP"
    # - optional sheet "DDP": Statut | DDP | Bien-fonds de base, from row 2
    try:
        wb = load_workbook(filename=BytesIO(file.read()))
    except Exception:
        return JsonResponse({"error": "Le fichier n'est pas un fichier Excel (.xlsx) valide."}, status=400)

    # sheet names are case-insensitive ("Balance", "BALANCE", "ddp", ...)
    sheets = {name.strip().lower(): wb[name] for name in wb.sheetnames}

    ws = sheets.get("balance")
    if ws is None:
        return JsonResponse(
            {"error": "Le fichier ne contient pas de feuille « Balance ». Utilisez un fichier généré avec « Télécharger (Excel) »."},
            status=400,
        )

    invalid_labels = []

    def _normalize(value):
        """Return the parcel label as displayed in the frontend ("<cadastre>_<number>", "DP", "RP")."""
        label = str(value).strip()
        if label.upper() in ("DP", "RP"):
            return label.upper()
        parts = label.split("_")
        if len(parts) != 2 or not all(part.isdigit() for part in parts):
            invalid_labels.append(label)
        return label

    def _sort_key(label):
        if label in ("DP", "RP"):
            return (1, [], label)
        try:
            return (0, [int(x) for x in label.split("_")], label)
        except ValueError:
            return (0, [], label)

    # new parcels (row 1, from column B)
    columns = {}
    j = 2
    while ws.cell(1, j).value is not None:
        columns[j] = _normalize(ws.cell(1, j).value)
        j += 1

    # old parcels (column A, from row 2)
    rows = {}
    i = 2
    while ws.cell(i, 1).value is not None:
        rows[i] = _normalize(ws.cell(i, 1).value)
        i += 1

    # DDP
    ddp = []
    ws_ddp = sheets.get("ddp")
    if ws_ddp is not None:
        for status, ddp_number, base in ws_ddp.iter_rows(min_row=2, max_col=3, values_only=True):
            if ddp_number is None or base is None:
                continue
            ddp.append(
                {
                    "relation": "-".join([_normalize(base), _normalize(ddp_number)]),
                    "immatriculation": not str(status or "").strip().lower().startswith("ex"),
                }
            )

    if invalid_labels:
        return JsonResponse(
            {
                "error": "Numéros de bien-fonds invalides (format attendu : <cadastre>_<numéro>, DP ou RP) : "
                + ", ".join(sorted(set(invalid_labels)))
            },
            status=400,
        )

    relations = set()
    for row_id, old in rows.items():
        for col_id, new in columns.items():
            value = ws.cell(row_id, col_id).value
            if value is not None and str(value).strip() != "":
                relations.add((old, new))

    old_bf = sorted(set(rows.values()), key=_sort_key)
    new_bf = sorted(set(columns.values()), key=_sort_key)

    balance = None
    if len(old_bf) > 0 and len(new_bf) > 0:
        # initialize balance 2d list, 1rst line and row for headers
        balance = [[" " for j in range(len(new_bf) + 1)] for i in range(len(old_bf) + 1)]
        for i, old in enumerate(old_bf):
            balance[i + 1][0] = old
        for j, new in enumerate(new_bf):
            balance[0][j + 1] = new

        for old, new in relations:
            balance[old_bf.index(old) + 1][new_bf.index(new) + 1] = "X"

    return JsonResponse({"balance": balance, "ddp": ddp})


@permission_required("parcel_historisation.view_designation", raise_exception=True)
def load_operation(request):
    """
    Load operation
    """
    operation_id = request.GET.get("operation")

    # check if operation_id already exists in database
    op = Operation.objects.get(id=operation_id)

    return JsonResponse(model_to_dict(op), safe=False)


class OperationViewSet(viewsets.ModelViewSet):
    """
    API endpoint that exposes operation in order to continue the edition mode
    """

    serializer_class = OperationSerializer

    def get_queryset(self):
        queryset = Operation.objects

        cadastre_id = self.request.query_params.get("cadastre_id")
        plan_link = self.request.query_params.get("plan_link")

        if plan_link and cadastre_id:
            queryset = queryset.filter(plan__link=plan_link, plan__cadastre=cadastre_id)

        return queryset


@permission_required("parcel_historisation.view_designation", raise_exception=True)
def liberate(request):
    """
    Liberate an operation (give again access to it)
    """
    id_ = request.GET.get("id")

    # check if operation_id already exists in database
    plan = Plan.objects.get(id=id_)
    plan.state = State(id=1)
    plan.save()

    return JsonResponse({"operation": 'saved'}, safe=False)


@permission_required("parcel_historisation.view_designation", raise_exception=True)
def run_control(request, cad_no):
    """
    Returns everything which is a source but has no destination (1)
    AND everything which is a destination but has no source (2)

    (1):
    SELECT src.source
    FROM parcel_historisation.balance src
    LEFT JOIN parcel_historisation.balance dst
    ON src.source = dst.destination
    WHERE dst.destination is null
    AND src.source like '14_%'
    GROUP BY src.source

    (2):
    SELECT dst.destination
    FROM parcel_historisation.balance src
    -- RIGHT JOIN (SELECT * FROM parcel_historisation.balance WHERE destination like '14_%') dst
    RIGHT JOIN parcel_historisation.balance dst
    ON src.source = dst.destination
    WHERE src.source is null
    AND dst.destination like '14_%'
    GROUP BY dst.destination
    """

    src = VBalanceSourceNoDest.objects.filter(source__contains=cad_no+"_").all()
    vbalancesourcenodest = []
    for row in src:
        vbalancesourcenodest.append(row.pk)

    dst = VBalanceDestNoSource.objects.filter(destination__contains=cad_no+"_").all()
    vbalancedestnosource = []
    for row in dst:
        vbalancedestnosource.append(row.pk)

    return JsonResponse({
        "operation": cad_no,
        "sources": vbalancesourcenodest,
        "destination": vbalancedestnosource}, safe=False)


@permission_required("parcel_historisation.view_designation", raise_exception=True)
def submit_control(request):
    """
    Process control types submitted by user in the control panel
    """

    data = json.loads(request.body)

    is_ok = False

    if data["type"] in ('rp_out', 'origin'):
        for item in data["source_bfs"]:
            balance = Balance()
            balance.immatriculation_ddp = False
            balance.exmatriculation_ddp = False
            balance.destination = item
            balance.source = 'origin'
            if data["type"] == 'rp_out':
                balance.source_rp = True
            else:
                balance.source_origin = True
            balance.save()

        is_ok = True

    if data["type"] in ('rp_in', 'final'):
        for item in data["dest_bfs"]:
            balance = Balance()
            balance.immatriculation_ddp = False
            balance.exmatriculation_ddp = False
            balance.source = item
            balance.destination = 'destination'
            if data["type"] == 'rp_in':
                balance.destination_rp = True
            else:
                balance.current_destination = True
            balance.save()

        is_ok = True

    saved = False
    if is_ok is True:
        balance.save()
        saved = True

    return JsonResponse(
        {
            "submitted": True,
            "saved": saved,
        }
    )
