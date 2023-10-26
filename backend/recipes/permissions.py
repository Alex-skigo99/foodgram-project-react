from rest_framework import permissions


class OwnerOrReadOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        return (
            request.method in permissions.SAFE_METHODS or request.user.is_authenticated
        )

    def has_object_permission(self, request, view, obj):
        return obj.author == request.user


class ReadOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.method in permissions.SAFE_METHODS


class MeOrAllowAny(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        print("request - ", request.request, "\nview - ", view, "\nobj -", obj)
        return obj == request.user
