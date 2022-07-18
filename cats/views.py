from dataclasses import asdict
from django.shortcuts import render
from django.http import HttpResponse
from django.template import loader
from django.db.models import Sum
from django.db.models.functions import Trunc
import json
from django.core.serializers.json import DjangoJSONEncoder
from cats.models import CATSAllYears

import datetime

def index(request):

    user = request.META['HTTP_REMOTE_USER']
    user = user.split('\\')[1]

    now = datetime.datetime.now()
    current_year = now.year

    years = []
    for i in range(current_year-3, current_year+1):
        years.append(i)

    template = loader.get_template('cats/index.html')
    context = {
        'user': user,
        'years': years
    }
    return HttpResponse(template.render(context, request))


def get_activity(request):
    
    user = request.META['HTTP_REMOTE_USER']
    user = user.split('\\')[1]

    cats = (CATSAllYears.objects.values('texte_imputation')
        .filter(username__contains=user)
        .annotate(year=Trunc('date', 'year'), hours=Sum('nombre_heure'))
    )

    cats = cats.all()

    now = datetime.datetime.now()

    current_year = now.year

    years = {}
    for i in range(current_year-3, current_year+1):
        years[i] = 0

    cats_list = list(cats)

    max = 0
    min = 2000
    grouped = {}
    for cat in cats_list:
        if cat['hours'] > max:
            max = cat['hours']
        if cat['hours'] != 0 and cat['hours'] < min:
            min = cat['hours']
        grouped.setdefault(cat['texte_imputation'], []).append(
            {k: v for k, v in cat.items() if k != 'texte_imputation'})

    result = []
    for group in grouped:
        this_years = years.copy()
        for year in grouped[group]:
            this_years[year['year'].year] = year['hours']
        
        subresult = []
        for v in this_years.values():
            subresult.append(v)
        result.append([
            group
        ]+subresult)
    
    results = {
        'data': result,
        'max': max,
        'min': min
    }

    json_data = json.dumps(results, cls=DjangoJSONEncoder)

    return HttpResponse(json_data, content_type='application/json')
