from django.contrib import admin

from .models import File


@admin.register(File)
class FileAdmin(admin.ModelAdmin):
    list_display = ('id', 'original_name', 'uploader', 'size', 'mime_type', 'created_at', 'is_deleted')
    list_filter = ('is_deleted', 'mime_type', 'created_at')
    search_fields = ('original_name', 'uploader__username')
