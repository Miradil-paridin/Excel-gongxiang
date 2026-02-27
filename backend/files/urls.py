"""files 应用 URL 配置"""

from django.urls import path

from . import views

urlpatterns = [
    path('files/', views.FileListCreateView.as_view(), name='file-list-create'),
    path('files/<int:pk>/', views.FileDetailView.as_view(), name='file-detail'),
    path('files/<int:pk>/restore/', views.FileRestoreView.as_view(), name='file-restore'),
    path('files/<int:pk>/download/', views.FileDownloadView.as_view(), name='file-download'),
    path('files/<int:pk>/open-in-editor/', views.FileOpenInEditorView.as_view(), name='file-open-in-editor'),
]
