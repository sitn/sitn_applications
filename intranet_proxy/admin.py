from django.contrib import admin
from intranet_proxy.models import VcronRoute

class VcronRouteAdmin(admin.ModelAdmin):
    ordering = ('url',)
admin.site.register(VcronRoute, VcronRouteAdmin)
