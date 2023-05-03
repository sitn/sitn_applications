from django.http import JsonResponse
from django.shortcuts import render
from cadastre.models import Cadastre


def get_cadastre(request):

    cadastres = Cadastre.objects.values('numcad', 'cadnom').all().order_by('cadnom')

    return JsonResponse(list(cadastres), safe=False)
