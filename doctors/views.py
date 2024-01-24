from django.http import HttpResponse
from django.shortcuts import get_object_or_404

from rest_framework import viewsets, generics
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.response import Response

from doctors.models import St21AvailableDoctorsWithGeom, St20AvailableDoctors
from doctors.serializers import St20AvailableDoctorsSerializer, DoctorEmailSerializer


class St20AvailableDoctorsViewSet(viewsets.ModelViewSet):
    queryset = St20AvailableDoctors.objects.all()
    serializer_class = St20AvailableDoctorsSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

    def list(self, request):
        return HttpResponse(
            St21AvailableDoctorsWithGeom.as_geojson(),
            headers={
                "Content-Type": "application/json",
            },
        )


class SuggestionView(generics.CreateAPIView):
    """
    Endpoint creating a Suggestion change.
    The suggestion is stored in the DB and an email is sent to the data owner.
    """

    def post(self, request, *args, **kwargs):
        #TODO
        pass


class GenerateMagicLinkView(generics.CreateAPIView):
    """
    Returns OK and generates a token that will be sent to further access
    a ressource in edit mode.
    """
    serializer_class = DoctorEmailSerializer
    queryset = St20AvailableDoctors.objects.all()

    def post(self, request, *args, **kwargs):
        serializer = DoctorEmailSerializer(data=request.data)
        queryset = self.get_queryset()
        obj = get_object_or_404(queryset, **serializer.initial_data)

        # TODO: generate token
        return Response('Ok')

