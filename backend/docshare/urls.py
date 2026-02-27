"""
URL configuration for docshare project.
"""

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/auth/', include('accounts.urls')),
    path('api/auth/', include('accounts.admin_urls')),
    path('api/', include('documents.urls')),
    path('api/', include('files.urls')),
    path('api/', include('shares.urls')),
    path('api/', include('workflow.urls')),
]

# 开发环境下的媒体文件服务
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
