"""
管理后台路由配置
"""
from django.urls import path
from . import admin_views

urlpatterns = [
    # 统计信息
    path('admin/statistics/', admin_views.AdminStatisticsView.as_view(), name='admin-statistics'),
    path('admin/dashboard/', admin_views.AdminDashboardView.as_view(), name='admin-dashboard'),

    # 用户管理
    path('admin/users/', admin_views.AdminUserListView.as_view(), name='admin-users'),
    path('admin/users/<int:pk>/', admin_views.AdminUserDetailView.as_view(), name='admin-user-detail'),
    path('admin/organizations/', admin_views.AdminOrganizationListCreateView.as_view(), name='admin-organizations'),
    path('admin/organizations/<int:pk>/', admin_views.AdminOrganizationDetailView.as_view(), name='admin-organization-detail'),
    path('admin/departments/', admin_views.AdminDepartmentListCreateView.as_view(), name='admin-departments'),
    path('admin/departments/<int:pk>/', admin_views.AdminDepartmentDetailView.as_view(), name='admin-department-detail'),
    path('admin/groups/', admin_views.AdminGroupListCreateView.as_view(), name='admin-groups'),
    path('admin/groups/<int:pk>/', admin_views.AdminGroupDetailView.as_view(), name='admin-group-detail'),

    # 文档管理
    path('admin/documents/', admin_views.AdminDocumentListView.as_view(), name='admin-documents'),
    path('admin/documents/<int:pk>/delete/', admin_views.AdminDocumentDeleteView.as_view(), name='admin-document-delete'),
    path('admin/documents/<int:pk>/force-delete/', admin_views.AdminDocumentForceDeleteView.as_view(), name='admin-document-force-delete'),

    # 文件管理
    path('admin/files/', admin_views.AdminFileListView.as_view(), name='admin-files'),
    path('admin/files/<int:pk>/delete/', admin_views.AdminFileDeleteView.as_view(), name='admin-file-delete'),
    path('admin/files/<int:pk>/force-delete/', admin_views.AdminFileForceDeleteView.as_view(), name='admin-file-force-delete'),

    # 分享管理
    path('admin/shares/', admin_views.AdminShareListView.as_view(), name='admin-shares'),
]
