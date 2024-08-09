from rest_framework.permissions import BasePermission

class IsUser(BasePermission):

    def has_permission(self,request,view):
        return request.user.is_user == True

class IsCompany(BasePermission):

    def has_permission(self,request,view):
        return request.user.is_company == True