from django.http import JsonResponse

from registre_foncier.models import RfcenAdresse

# Create your views here.
def index(request):
    """
    Serving the base template.
    """
    ttt = RfcenAdresse.objects.using("terris").values('akt_name', 'akt_vorname').first()

    return JsonResponse(ttt, safe=False)
