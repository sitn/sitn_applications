from django.contrib import admin
from health.models import St20AvailableDoctors, St21AvailableDoctorsWithGeom


class St20AvailableDoctorsAdmin(admin.ModelAdmin):
    model = St20AvailableDoctors
    search_fields = ['doctor__id_person_address', 'doctor__nom', 'doctor__prenoms']
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

admin.site.register(St20AvailableDoctors, St20AvailableDoctorsAdmin)
admin.site.register(St21AvailableDoctorsWithGeom, St21AvailableDoctorsWithGeomAdmin)
