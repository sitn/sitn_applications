from django.conf import settings
from django.core.exceptions import BadRequest
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.utils import timezone

from rest_framework import viewsets, mixins, status, permissions, generics
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView

from sitn.tools.emailer import send_email
from health.models import (
    St21AvailableDoctorsWithGeom,
    St20AvailableDoctors,
    St22DoctorChangeSuggestion,
    St23HealthSite
)
from health.serializers import (
    St20AvailableDoctorsSerializer,
    DoctorEmailSerializer,
    St21AvailableDoctorsWithGeomSerializer,
    St22DoctorChangeSuggestionSerializer,
    St23HealthSiteSerializer
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
        data = St21AvailableDoctorsWithGeom.as_geojson()
        return JsonResponse(
            data, 
            safe=False,
            json_dumps_params={'ensure_ascii': False}
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
        if obj.login_email.lower() != serializer.data.get('login_email').lower():
            obj.save()
            send_email(
                "Modification de vos informations cartographie SITN",
                to=serializer.data.get('login_email'),
                template_name="email_not_found",
                template_data={
                    "company_name": "Service de la santé publique",
                    "address_1": "Rue des Beaux-Arts 13",
                    "address_2": "2000 Neuchâtel",
                    "phone_number": "032 889 62 00",
                    "email": "scsp.opam@ne.ch"
                },
            )
            return Response("ok")

        # Generate GUID if previous controls pass
        obj.prepare_for_edit()
        url = f"{settings.HEALTH.get('front_url')}?guid={obj.edit_guid}"
        send_email(
            "Modification de vos informations cartographie SITN",
            to=obj.login_email,
            template_name="email_magic_link",
            template_data={"url": url},
        )
        obj.save()
        return Response("ok")


class DoctorsByTokenView(APIView):
    authentication_classes = []

    def get(self, request, token):
        queryset = St20AvailableDoctors.objects.all()
        editable_doctor = get_object_or_404(queryset, edit_guid=token)
        if not editable_doctor.is_edit_guid_valid:
            return Response(status=410)
        queryset = St21AvailableDoctorsWithGeom.objects.all()
        doctor_infos = get_object_or_404(queryset, pk=editable_doctor.pk)
        serializer = St21AvailableDoctorsWithGeomSerializer(doctor_infos, context={'request': request})
        return Response(serializer.data)

    def put(self, request, token):
        queryset = St20AvailableDoctors.objects.all()
        item = get_object_or_404(queryset, edit_guid=token)
        if not item.is_edit_guid_valid:
            return Response(status=status.HTTP_410_GONE)
        serializer = St20AvailableDoctorsSerializer(item, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(status=status.HTTP_202_ACCEPTED)
        raise BadRequest(serializer.errors)


class St22DoctorChangeSuggestionView(generics.CreateAPIView):
    """
    Anonymous user suggestion
    """
    permission_classes = [permissions.AllowAny]
    authentication_classes = []
    allowed_methods = ['POST', 'OPTIONS', 'HEAD']

    def get_serializer(self, *args, **kwargs):
        return St22DoctorChangeSuggestionSerializer(*args, **kwargs)
    
    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        doctor = serializer.validated_data.get('doctor')
        # No more than 3 suggestions per doctor
        existing_suggestions = St22DoctorChangeSuggestion.objects.filter(is_done=False, doctor=doctor).count()
        if existing_suggestions > 2:
            return Response(status=status.HTTP_429_TOO_MANY_REQUESTS)
        serializer.save()
        return Response(status=status.HTTP_201_CREATED)


class St23HealthSiteViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = St23HealthSite.objects.all()
    serializer_class = St23HealthSiteSerializer
    paginator = None
