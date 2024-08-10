from rest_framework.permissions import BasePermission

class IsUser(BasePermission):
    """
    Custom permission to allow access only to users.
    """

    def has_permission(self, request, view):
        # Check if their 'is_user' attribute is True
        return request.user.is_user is True

class IsCompany(BasePermission):
    """
    Custom permission to allow access only to companies.
    """

    def has_permission(self, request, view):
        # Check  if their 'is_company' attribute is True
        return request.user.is_company is True
