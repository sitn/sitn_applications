from django.views.generic import TemplateView

class HelpView(TemplateView):
    template_name = "help_ecap.html"
