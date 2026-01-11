from django.shortcuts import render
from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticated
from trips.permissions import IsTripCreator
from accounts.permissions import IsIndividualDriver, IsCompanyDriver
from trips.models import Trip
from trips.serializers import TripSerializer, TripAssignSerializer
from rest_framework import filters, mixins, viewsets, status
from rest_framework.response import Response
from django.utils import timezone
from rest_framework.decorators import action
import hashlib
import random


# Create your views here.


class TripViewSet(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    viewsets.GenericViewSet,
):
    permission_classes = [IsAuthenticated, IsTripCreator]
    queryset = Trip.objects.all()
    serializer_class = TripSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = [
        "creator__name",
        "driver__name",
        "vehicle__license_number",
        "vehicle__registration_number",
    ]

    def get_queryset(self):
        return self.queryset.filter(company=self.request.user)

    def perform_create(self, serializer):
        serializer.save(company=self.request.user)

    @action(
        detail=True,
        methods=["post"],
    )
    def assign(
        self, request, pk=None, permission_classes=[IsIndividualDriver, IsTripCreator]
    ):
        trip = self.get_object()
        if trip.status != Trip.Status.PENDING:
            return Response(
                {"error": "Trip not pending"}, status=status.HTTP_400_BAD_REQUEST
            )
        if trip.status == Trip.Status.ASSIGNED:
            return Response(
                {"error": "Trip already assigned"}, status=status.HTTP_400_BAD_REQUEST
            )
        serializer = TripAssignSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        trip.otp_code = str(random.randint(100000, 999999))
        trip.driver = serializer.validated_data["driver"]
        trip.status = Trip.Status.ASSIGNED
        trip.assigned_at = timezone.now()
        trip.save(update_fields=["otp_code", "driver", "status", "assigned_at"])
        return Response({"message": "Trip assigned"}, status=status.HTTP_200_OK)

    @action(
        detail=True,
        methods=["post"],
        permission_classes=[IsCompanyDriver, IsIndividualDriver],
    )
    def start(self, request, pk=None):
        trip = self.get_object()
        if trip.status != Trip.Status.ASSIGNED:
            return Response(
                {"error": "Trip not assigned"}, status=status.HTTP_400_BAD_REQUEST
            )
        trip.status = Trip.Status.IN_PROGRESS
        trip.started_at = timezone.now()
        trip.save(update_fields=["status", "started_at"])
        return Response({"message": "Trip started"}, status=status.HTTP_200_OK)

    @action(detail=True, methods=["post"])
    def confirm(self, request, pk=None):
        trip = self.get_object()
        if trip.otp_code is None:
            return Response(
                {"error": "OTP not sent"}, status=status.HTTP_400_BAD_REQUEST
            )
        if trip.otp_code != request.data.get("otp"):
            return Response(
                {"error": "Invalid OTP"}, status=status.HTTP_400_BAD_REQUEST
            )
        trip.status = Trip.Status.COMPLETED
        trip.completed_at = timezone.now()
        trip.otp_code = None
        trip.save(update_fields=["status", "completed_at", "otp_code"])
        return Response({"message": "OTP confirmed"}, status=status.HTTP_200_OK)

    @action(
        detail=True,
        methods=["post"],
        permission_classes=[IsCompanyDriver, IsIndividualDriver],
    )
    def cancel(self, request, pk=None):
        trip = self.get_object()
        if trip.status != Trip.Status.PENDING:
            return Response(
                {"error": "Trip not pending"}, status=status.HTTP_400_BAD_REQUEST
            )
        trip.otp_code = None
        trip.status = Trip.Status.CANCELLED
        trip.cancelled_at = timezone.now()
        trip.save(update_fields=["otp_code", "status", "cancelled_at"])
        return Response({"message": "Trip cancelled"}, status=status.HTTP_200_OK)
