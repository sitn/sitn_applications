"""sitn URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import include, path, re_path
from django.conf import settings
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView, SpectacularRedocView
from sitn.router import SitnRouter

router = SitnRouter()


router.register_app('cadastre', '/cadastre/')
urlpatterns = [
    path('schema/', SpectacularAPIView.as_view(), name='schema'),
    path('schema/swagger-ui/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('schema/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
    path('admin/', admin.site.urls),
    path('', router.get_api_root_view(), name='api-root'),
    path('cadastre/', include('cadastre.urls')),
]

if settings.IS_INTRANET:
    router.register_app('ecap_intra', '/ecap/')
    router.register_app('cats', '/cats/')
    router.register_app('parcel_historisation', '/parcel_historisation/')
    router.register_app('intranet_proxy', '/intranet_proxy/')
    urlpatterns.extend([
        path('ecap/', include('ecap_intra.urls')),
        path('cats/', include('cats.urls')),
        path('parcel_historisation/', include('parcel_historisation.urls')),
        re_path(r'(?:vcron|intranet)_proxy/', include('intranet_proxy.urls')),
    ])
else:
    router.register_app('ecap', '/ecap/')
    router.register_app('action_sociale', '/action_sociale/')
    router.register_app('health', '/health/')
    router.register_app('roads', '/roads/')
    router.register_app('stationnement', '/stationnement/')
    router.register_app('forest_forpriv', '/forest_forpriv/')
    urlpatterns.extend([
        path('ecap/', include('ecap.urls')),
        path('action_sociale/', include('action_sociale.urls')),
        path('health/', include('health.urls')),
        path('roads/', include('roads.urls')),
        path('stationnement/', include('stationnement.urls')),
        path('forest_forpriv/', include('forest_forpriv.urls')),
    ])
