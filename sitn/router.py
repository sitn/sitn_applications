from rest_framework.routers import DefaultRouter
from rest_framework.response import Response
from rest_framework.reverse import reverse
from rest_framework.decorators import api_view
from collections import OrderedDict


class SitnRouter(DefaultRouter):
    """
    Extension of DefaultRouter to add more urls to Root
    """
    def __init__(self):
        super().__init__()
        self.additional_views = []
        self.registered_apps = []
    
    def register_additional_view(self, prefix, name):
        """
        Allows to add more routes to DefaultApiRoot
        """
        self.additional_views.append({
            'prefix': prefix,
            'name': name
        })
    
    def register_app(self, app_name, url_prefix=None):
        """
        Will register a link to a sub app
        """
        if url_prefix is None:
            url_prefix = f'/{app_name}/'
        self.registered_apps.append({
            'name': app_name,
            'url_prefix': url_prefix
        })
    
    def get_api_root_view(self, api_urls=None):
        """
        Return a basic root view.
        """
        api_root_dict = OrderedDict()
        list_name = self.routes[0].name
        for prefix, viewset, basename in self.registry:
            api_root_dict[prefix] = list_name.format(basename=basename)
        
        for view in self.additional_views:
            api_root_dict[view['prefix']] = view['name']
        
        registered_apps = self.registered_apps
        
        @api_view(['GET'])
        def api_root(request, format=None):
            ret = OrderedDict()
            
            for key, url_name in api_root_dict.items():
                ret[key] = reverse(url_name, request=request, format=format)
            
            for app in registered_apps:
                ret[app['name']] = request.build_absolute_uri(app['url_prefix'])
            
            return Response(ret)
        
        return api_root
