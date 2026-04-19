from rest_framework import permissions


class UserManagementPermission(permissions.BasePermission):
    """员工可管理全部用户；普通用户仅可查看/修改自身。"""

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        if view.action == "create":
            return request.user.is_staff
        return True

    def has_object_permission(self, request, view, obj):
        if request.user.is_staff:
            return True
        return obj.pk == request.user.pk
