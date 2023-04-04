from django.http import HttpResponse
from intranet_proxy.session import GeoshopSession

def get_metadata(request, path):
    geoshop_session = GeoshopSession()
    response = geoshop_session.http_get(f'metadata/{path}')
    return HttpResponse(response.content)
