from django.shortcuts import render
from rest_framework.generics import RetrieveUpdateAPIView
from accounts.permissions import IsCompanyDriver
from accounts.serializers import DriverOnlineStatusSerializer
from rest_framework.permissions import IsAuthenticated


# Create your views here.


class DriverOnlineStatusView(RetrieveUpdateAPIView):
    permission_classes = [IsAuthenticated, IsCompanyDriver]
    serializer_class = DriverOnlineStatusSerializer

    def get_object(self):
        return self.request.user.driver_profile
