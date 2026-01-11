from django.shortcuts import render
from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticated
from accounts.permissions import IsCompanyDriver, IsIndividualDriver
from vehicles.models import Vehicle
from vehicles.serializers import VehicleSerializer
from rest_framework import filters

# Create your views here.


class VehicleViewSet(ModelViewSet):
    permission_classes = [IsAuthenticated, IsCompanyDriver, IsIndividualDriver]
    queryset = Vehicle.objects.all()
    serializer_class = VehicleSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ["brand", "model", "license_number", "registration_number"]

    def get_queryset(self):
        return self.queryset.filter(driver=self.request.user)

    def perform_create(self, serializer):
        serializer.save(driver=self.request.user)
