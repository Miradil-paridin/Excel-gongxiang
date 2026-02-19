"""
自定义权限类
"""

from rest_framework import permissions


class IsAdminOrReadOnly(permissions.BasePermission):
    """
    只允许管理员进行写操作，其他用户只读
    """

    def has_permission(self, request, view):
        # 读取请求允许所有认证用户
        if request.method in permissions.SAFE_METHODS:
            return request.user and request.user.is_authenticated

        # 写入请求只允许管理员
        return request.user and request.user.is_staff


class IsOwnerOrAdmin(permissions.BasePermission):
    """
    只允许资源所有者或管理员访问
    """

    def has_object_permission(self, request, view, obj):
        # 管理员可以访问所有资源
        if request.user.is_staff:
            return True

        # 检查用户是否是资源所有者
        # 对于User对象，检查是否是自己
        if hasattr(obj, 'user'):
            return obj.user == request.user
        elif hasattr(obj, 'creator'):
            return obj.creator == request.user
        elif hasattr(obj, 'uploader'):
            return obj.uploader == request.user

        # 默认情况下只允许管理员
        return False


class IsAdminUser(permissions.BasePermission):
    """
    只允许管理员访问
    """

    def has_permission(self, request, view):
        return request.user and request.user.is_staff
