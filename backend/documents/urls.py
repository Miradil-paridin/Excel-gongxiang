"""
documents 应用 URL 配置
"""

from django.urls import path
from . import views
from .callback_views import document_callback

urlpatterns = [
    # 文档列表和创建
    path('documents/', views.DocumentListCreateView.as_view(), name='document-list'),
    # 文档详情、更新、删除
    path('documents/<int:pk>/', views.DocumentDetailView.as_view(), name='document-detail'),
    # 恢复已删除文档
    path('documents/<int:pk>/restore/', views.DocumentRestoreView.as_view(), name='document-restore'),
    # OnlyOffice 编辑器配置
    path('documents/<int:pk>/editor-config/', views.DocumentEditorConfigView.as_view(), name='editor-config'),
    # OnlyOffice 回调
    path('documents/callback/', document_callback, name='callback'),
]
