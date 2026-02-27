from django.contrib import admin
from .models import Organization, Department, UserProfile


@admin.register(Organization)
class OrganizationAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'code', 'is_active', 'created_at')
    search_fields = ('name', 'code')
    list_filter = ('is_active',)


@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'organization', 'code', 'parent', 'is_active')
    search_fields = ('name', 'code', 'organization__name')
    list_filter = ('is_active', 'organization')


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'organization', 'department', 'role_title', 'updated_at')
    search_fields = ('user__username', 'user__email', 'role_title')
    list_filter = ('organization', 'department')
