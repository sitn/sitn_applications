from django.contrib import admin
from health.models import (
    St20AvailableDoctors,
    St21AvailableDoctorsWithGeom,
    St22DoctorChangeSuggestion,
    St23HealthSite
)


class St20AvailableDoctorsAdmin(admin.ModelAdmin):
    model = St20AvailableDoctors
    search_fields = ['doctor__id_person_address', 'doctor__nom', 'doctor__prenoms']
    readonly_fields = ['login_email', 'doctor']
    list_display = [
        'pk',
        'nom',
        'prenoms',
        'address',
        'nopostal',
        'localite',
    ]
    raw_id_fields = ['doctor']
    exclude = []
    ordering = ['-pk']

    def get_queryset(self, *args, **kwargs):
        return super().get_queryset(*args, **kwargs).filter(
            doctor__nom__isnull=False
        )

    def nom(self, instance):
        return instance.doctor.nom

    def prenoms(self, instance):
        return instance.doctor.prenoms

    def address(self, instance):
        return instance.doctor.address

    def nopostal(self, instance):
        return instance.doctor.nopostal

    def localite(self, instance):
        return instance.doctor.localite


class St21AvailableDoctorsWithGeomAdmin(admin.ModelAdmin):
    model = St21AvailableDoctorsWithGeom
    search_fields = [
        'pk',
        'nom',
        'prenoms'
    ]
    list_display = [
        'pk',
        'nom',
        'prenoms',
        'address',
        'nopostal',
        'localite',
    ]


class St22DoctorChangeSuggestionAdmin(admin.ModelAdmin):
    model = St22DoctorChangeSuggestion
    list_filter = ['is_done']
    list_display = [
        'pk',
        'doctor',
        'requested_when',
        'is_done',
    ]
    ordering = ['is_done']


class St23HealthSiteAdmin(admin.ModelAdmin):
    model = St23HealthSite
    list_display = [
        'site_name',
        'address',
    ]
    ordering = ['site_name']

admin.site.register(St22DoctorChangeSuggestion, St22DoctorChangeSuggestionAdmin)
admin.site.register(St20AvailableDoctors, St20AvailableDoctorsAdmin)
admin.site.register(St23HealthSite, St23HealthSiteAdmin)
