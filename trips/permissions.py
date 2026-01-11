from rest_framework.permissions import BasePermission
from trips.models import Trip
from rest_framework.permissions import SAFE_METHODS


class IsTripCreator(BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return True
        return obj.company == request.user
