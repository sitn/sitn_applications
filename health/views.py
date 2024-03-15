from django.conf import settings
from django.core.exceptions import BadRequest
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.utils import timezone

from rest_framework import viewsets, mixins
from rest_framework.decorators import action, api_view
from rest_framework.response import Response

from sitn.tools.emailer import send_email
from health.models import St21AvailableDoctorsWithGeom, St20AvailableDoctors
from health.serializers import (
    St20AvailableDoctorsSerializer,
    DoctorEmailSerializer,
    St21AvailableDoctorsWithGeomSerializer
)

class St20AvailableDoctorsViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    viewsets.GenericViewSet,
):
    authentication_classes = []
    queryset = St20AvailableDoctors.objects.all()
    serializers = {
        "default": St20AvailableDoctorsSerializer,
        "request_change": DoctorEmailSerializer
    }

    def get_serializer_class(self):
        return self.serializers.get(self.action, self.serializers["default"])

    @action(detail=False, methods=["get"])
    def as_geojson(self, request):
        return HttpResponse(
            St21AvailableDoctorsWithGeom.as_geojson(),
            headers={
                "Content-Type": "application/json",
            },
        )

    @action(detail=True, methods=["post"])
    def request_change(self, request, pk):
        queryset = self.get_queryset()
        obj = get_object_or_404(queryset, pk=pk)
        serializer = DoctorEmailSerializer(data=request.data)

        if not serializer.is_valid():
            raise BadRequest("Invalid data")

        # Do not allow multiple requests within a short duration
        if obj.has_been_requested_recently:
            return Response(status=429)

        # If email not found, send email to explain
        obj.guid_requested_when = timezone.now()
        if obj.login_email != serializer.data.get('login_email'):
            obj.save()
            send_email(
                "Modification de vos informations",
                to=serializer.data.get('login_email'),
                template_name="email_not_found",
                template_data={
                    "company_name": "Service de la santé publique",
                    "address_1": "Rue des Beaux-Arts 13",
                    "address_2": "2000 Neuchâtel",
                    "phone_number": "032 889 62 00",
                    "email": "Service.SantePublique@ne.ch"
                },
            )
            return Response("ok")

        # Generate GUID if previous controls pass
        if obj.login_email == serializer.data.get('login_email'):
            obj.prepare_for_edit()
            url = f"{settings.HEALTH.get('front_url')}?guid={obj.edit_guid}"
            send_email(
                "Modification de vos informations",
                to=obj.login_email,
                template_name="email_magic_link",
                template_data={"url": url},
            )
            obj.save()
            return Response("ok")


@api_view(['GET'])
def get_doctor_by_token(request, token):
    queryset = St20AvailableDoctors.objects.all()
    editable_doctor = get_object_or_404(queryset, edit_guid=token)
    if not editable_doctor.is_edit_guid_valid:
        return Response(status=410)
    queryset = St21AvailableDoctorsWithGeom.objects.all()
    doctor_infos = get_object_or_404(queryset, pk=editable_doctor.pk)
    serializer = St21AvailableDoctorsWithGeomSerializer(doctor_infos, context={'request': request})
    return Response(serializer.data)

# TODO: Move this to an api view class
@api_view(['PUT'])
def put_doctor_by_token(request, token):
    queryset = St20AvailableDoctors.objects.all()
    item = get_object_or_404(queryset, edit_guid=token)
    if not item.is_edit_guid_valid:
        return Response(status=410)
    serializer = St20AvailableDoctorsSerializer(item, data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response("ok")
    raise BadRequest(serializer.errors)
