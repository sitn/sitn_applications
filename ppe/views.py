from django.shortcuts import get_object_or_404, render
from django.http import HttpResponse
from django.template import loader

from .models import DossierPPE
from .forms import DossierPPEForm

def index(request):
    latest_dossiers_list = DossierPPE.objects.order_by("-date_creation")[:5]
    template = loader.get_template("ppe/index.html")
    context = {
        "latest_dossiers_list": latest_dossiers_list,
    }
    return HttpResponse(template.render(context, request))

def detail(request, id):
    dossier_ppe = get_object_or_404(DossierPPE, pk=id)
    return render(request, "ppe/detail.html", {"dossier_ppe": dossier_ppe})

def confirmation(request):
    try:
        choice = request.POST["choix"]
    except KeyError:
        # Redisplay the question voting form.
        return render(
            request,
            "ppe/confirmation.html",
            {
                "error_message": "You didn't select a choice.",
            },
        )
    if choice == 'depot':
        form = DossierPPEForm()
        return render(request, "ppe/ol.html", {"form": DossierPPEForm})
    else:
        return render(request, "ppe/confirmation.html", {"choix": choice})