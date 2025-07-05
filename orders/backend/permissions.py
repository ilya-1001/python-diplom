from rest_framework import permissions
from rest_framework.permissions import BasePermission
from rest_framework.exceptions import PermissionDenied


class IsAuthenticatedAndSupplier(BasePermission):
    """
    Разрешает доступ только аутентифицированным пользователям с типом supplier.
    """
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and request.user.type == 'supplier')


class IsAuthenticatedAndBuyer(BasePermission):
    """
    Разрешает доступ только аутентифицированным пользователям с типом buyer.
    """
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and request.user.type == 'buyer')


class IsManagerOrReadOnly(BasePermission):

    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user.is_manager

    def message(self, request):
        if request.method in permissions.SAFE_METHODS:
            return "You do not have permission to modify this resource."
        else:
            return "Manager access is required to create or update resources."
