from rest_framework.permissions import BasePermission
from accounts.models import User


class IsAdmin(BasePermission):
    def has_permission(self, request, view):
        return request.user.role == User.Role.ADMIN


class IsCompanyOwner(BasePermission):
    def has_permission(self, request, view):
        return request.user.role == User.Role.COMPANY_OWNER


class IsCompanyDriver(BasePermission):
    def has_permission(self, request, view):
        return request.user.role == User.Role.COMPANY_DRIVER


class IsIndividualDriver(BasePermission):
    def has_permission(self, request, view):
        return request.user.role == User.Role.INDIVIDUAL_DRIVER
