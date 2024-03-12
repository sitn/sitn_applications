from datetime import timedelta

from django.conf import settings
from django.core.exceptions import BadRequest
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt

from rest_framework import viewsets, mixins, generics
from rest_framework.decorators import action
from rest_framework.response import Response

from sitn.tools.emailer import send_email
from health.models import St21AvailableDoctorsWithGeom, St20AvailableDoctors
from health.serializers import (
    St20AvailableDoctorsSerializer,
    DoctorEmailSerializer,
)

@method_decorator(csrf_exempt, name='dispatch')
class St20AvailableDoctorsViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    viewsets.GenericViewSet,
):
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

        # Do not allow multiple requests within 3 days
        if obj.guid_requested_when:
            now = timezone.now()
            three_days_ago = now - timedelta(days=3)
            if obj.guid_requested_when > three_days_ago:
                return Response(status=429)

        obj.guid_requested_when = timezone.now()

        # If email not found, send email to explain
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


class St20DoctorsByTokenView(generics.RetrieveUpdateAPIView):
    queryset = St20AvailableDoctors.objects.all()
    serializer_class = St20AvailableDoctorsSerializer

    def get(self, request, token):
        queryset = self.get_queryset()
        item = get_object_or_404(queryset, edit_guid=token)
        serializer = St20AvailableDoctorsSerializer(item, context={'request': request})
        return Response(serializer.data)

    def put(self, request, token):
        queryset = self.get_queryset()
        item = get_object_or_404(queryset, edit_guid=token)
        serializer = St20AvailableDoctorsSerializer(item, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response("ok")
        raise BadRequest(serializer.errors)