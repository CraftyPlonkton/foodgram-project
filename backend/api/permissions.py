from rest_framework.permissions import SAFE_METHODS, BasePermission


class ListPostAllowAny(BasePermission):
    def has_permission(self, request, view):
        return request.method in ['POST', *SAFE_METHODS]

    def has_object_permission(self, request, view, obj):
        return request.user.is_authenticated


class GetAllowAnyIsOwnerOrReadOnly(BasePermission):
    def has_permission(self, request, view):
        return (request.method in SAFE_METHODS or
                request.user.is_authenticated)

    def has_object_permission(self, request, view, obj):
        return (request.method in SAFE_METHODS or
                request.user.id == obj.author.id)
