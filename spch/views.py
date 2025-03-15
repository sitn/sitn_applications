from django.views.generic import TemplateView

# Create your views here.
class HelpView(TemplateView):
    template_name = "help_spch.html"
