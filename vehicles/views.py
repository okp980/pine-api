from django.shortcuts import render
from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticated
from accounts.permissions import IsCompanyDriver, IsIndividualDriver
from vehicles.models import Vehicle
from vehicles.serializers import VehicleSerializer

# Create your views here.


class VehicleViewSet(ModelViewSet):
    permission_classes = [IsAuthenticated, IsCompanyDriver, IsIndividualDriver]
    queryset = Vehicle.objects.all()
    serializer_class = VehicleSerializer

    def get_queryset(self):
        return self.queryset.filter(driver=self.request.user)
