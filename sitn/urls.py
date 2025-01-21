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

urlpatterns = [
    path('schema/', SpectacularAPIView.as_view(), name='schema'),
    path('schema/swagger-ui/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('schema/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
    path('admin/', admin.site.urls),
    path('cadastre/', include('cadastre.urls')),
]

if settings.IS_INTRANET:
    urlpatterns.extend([
        path('ecap/', include('ecap.urls')),
        path('cats/', include('cats.urls')),
        path('parcel_historisation/', include('parcel_historisation.urls')),
        re_path(r'(?:vcron|intranet)_proxy/', include('intranet_proxy.urls')),
    ])
else:
    urlpatterns.extend([
        path('health/', include('health.urls')),
        path('stationnement/', include('stationnement.urls')),
        path('forest_forpriv/', include('forest_forpriv.urls')),
    ])
