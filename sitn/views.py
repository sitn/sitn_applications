import logging

from django.shortcuts import render

LOGGER = logging.getLogger(__name__)
def index(request):
    """
    Vue de test de l'authentification
    """
    LOGGER.info(f'INDEX has been accessed with user: {request.user}')
    return render(request, 'test-auth.html')