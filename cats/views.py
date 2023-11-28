from dataclasses import asdict
from django.shortcuts import render
from django.http import HttpResponse
from django.template import loader
from django.db.models import Sum, CharField, Value
from django.db.models.functions import Trunc, Concat
import json
from django.core.serializers.json import DjangoJSONEncoder
from cats.models import CATSAllYears

import datetime

def index(request):

    user = request.META['HTTP_REMOTE_USER']
    user = user.split('\\')[1]
    user = user.lower()

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
    user = user.lower()

    now = datetime.datetime.now()

    current_year = now.year

    years = {}
    for i in range(current_year-3, current_year+1):
        years[i] = 0
    
    cats = (CATSAllYears.objects.values('texte_imputation', 'imputation_multiple')
        .filter(username__contains=user)
        .filter(date__gte=str(current_year-3)+'-01-01')
        .annotate(
            year=Trunc('date', 'year'),
            hours=Sum('nombre_heure'),
            label=Concat('texte_imputation', Value(' - '), 'imputation_multiple', output_field=CharField())
            )
        .order_by('texte_imputation', 'imputation_multiple')
    )

    cats = cats.all()

    cats_list = list(cats)

    max = 0
    min = 2000
    grouped = {}
    for cat in cats_list:
        if cat['hours'] > max:
            max = cat['hours']
        if cat['hours'] != 0 and cat['hours'] < min:
            min = cat['hours']

        if cat['label'][-3:] == ' - ':
            cat['label'] = cat['label'][:-3]

        grouped.setdefault(cat['label'], []).append(
            {k: v for k, v in cat.items() if k != 'label'})

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
