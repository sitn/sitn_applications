from django.http import JsonResponse, HttpResponseBadRequest

from registre_foncier.models import RfcenAdresse, Recht

# Create your views here.
def index(request):
    """
    Serving the base template.
    """
    ttt = RfcenAdresse.objects.values('akt_name', 'akt_vorname').first()

    return JsonResponse(ttt, safe=False)

def parcel_dependencies(request):
    """
    Retrieves the first parent of a proprety (if exists)
    It does not retrive all the hierarchy, only the first level

    params:
    - cadastre: cadastre number (integer)
    - parcel: parcel number (without the # or the cadastre number)
    """

    if "cadastre" not in request.GET:
        return HttpResponseBadRequest("No cadastre")

    if "parcel" not in request.GET:
        return HttpResponseBadRequest("No parcel number")
    
    typ_imm = {
        '1': 'BF',
        '2': 'DDP',
        '3': 'Mine',
        '4': 'PPE',
        '5': 'COP',
    }
    
    cadastre = request.GET['cadastre']
    parcel = request.GET['parcel']
    parcel = parcel.strip()

    result = {
        'valid': True,
        'data': {
            'parcel': parcel,
            'cadastre': cadastre,
            'parents': [],
        }
    }

    parcel_s = parcel.split('/')
    parcel = '#' + parcel_s[0].rjust(8, ' ')

    if len(parcel_s) > 1:
        parcel += '/' + parcel_s[1]

    # Check that it is a valid parcel
    check = Recht.objects.filter(lst_typ='E', esta_last=cadastre, gdk_last=parcel, loesch_status__isnull=True).all()

    if len(check) == 0:
        result['valid'] = False
        return JsonResponse({'data':result}, safe=False)

    base = check[0]
    result['data']['type'] = typ_imm[base.art_last]

    # PPE
    parents  = Recht.objects.filter(lst_typ='E', esta_recht=cadastre, gdk_recht=parcel, loesch_status__isnull=True).all()

    if len(parents) > 0:
        parent = parents[0]
        parent_s = parents[0].gdk_last.replace('#', '').strip()

        result['data']['parents'].append({
            'parcel': parent_s,
            'cadastre': parent.esta_last,
            'type': typ_imm[parent.art_last],
        })

    # COP
    parents  = Recht.objects.filter(lst_typ='D', art_last='1', esta_recht=cadastre, gdk_recht=parcel, loesch_status__isnull=True).all()

    for parent in parents:
        parent_s = parent.gdk_last.replace('#', '').strip()

        result['data']['parents'].append({
            'parcel': parent_s,
            'cadastre': parent.esta_last,
            'type': typ_imm[parent.art_last],
        })

    return JsonResponse({'data':result}, safe=False)
