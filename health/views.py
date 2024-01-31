from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.core.exceptions import BadRequest

from rest_framework import viewsets, mixins
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.response import Response

from sitn.tools.emailer import send_email
from health.models import St21AvailableDoctorsWithGeom, St20AvailableDoctors
from health.serializers import (
    St20AvailableDoctorsSerializer,
    DoctorEmailSerializer,
    DoctorUUIDSerializer,
)


class St20AvailableDoctorsViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    viewsets.GenericViewSet,
):
    queryset = St20AvailableDoctors.objects.all()
    permission_classes = [IsAuthenticatedOrReadOnly]
    serializers = {
        "default": St20AvailableDoctorsSerializer,
        "update": DoctorUUIDSerializer,
        "request_change": DoctorEmailSerializer
    }

    def get_serializer_class(self):
        return self.serializers.get(self.action, self.serializers["default"])

    def list(self, request):
        return HttpResponse(
            St21AvailableDoctorsWithGeom.as_geojson(),
            headers={
                "Content-Type": "application/json",
            },
        )

    @action(detail=True, methods=["post"])
    def request_change(self, request, pk):
        serializer = DoctorEmailSerializer(data=request.data)
        queryset = self.get_queryset()
        if serializer.is_valid():
            obj = get_object_or_404(queryset, **serializer.initial_data)
            if obj:
                obj.prepare_for_edit()
                send_email(
                    "Modification de vos informations",
                    to=obj.login_email,
                    template_name="email_magic_link",
                    template_data={"guid": obj.edit_guid},
                )
                obj.save()
            return Response("Found")
        raise BadRequest

    def update(self, request, pk=None):
        queryset = self.get_queryset()
        obj = get_object_or_404(queryset, pk=pk)
        serializer = DoctorUUIDSerializer(obj, data=request.data)
        try:
            edit_guid = serializer.initial_data.pop('edit_guid')
        except KeyError:
            raise BadRequest("No edit_guid provided")
        if serializer.is_valid():
            if edit_guid == str(obj.edit_guid):
                serializer.save()
                return Response("ok")
            raise BadRequest("Invalid edit_guid")
        raise BadRequest(serializer.errors)
