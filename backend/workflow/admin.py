from django.contrib import admin

from .models import DistributionTask, Submission, TaskAssignment, Template


@admin.register(Template)
class TemplateAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'category', 'version', 'is_active', 'created_by', 'updated_at')
    list_filter = ('is_active', 'category')
    search_fields = ('name', 'category', 'created_by__username')


@admin.register(DistributionTask)
class DistributionTaskAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'template', 'status', 'deadline', 'created_by', 'created_at')
    list_filter = ('status',)
    search_fields = ('title', 'template__name', 'created_by__username')


@admin.register(TaskAssignment)
class TaskAssignmentAdmin(admin.ModelAdmin):
    list_display = ('id', 'task', 'assignee', 'status', 'submitted_at', 'updated_at')
    list_filter = ('status',)
    search_fields = ('task__title', 'assignee__username')


@admin.register(Submission)
class SubmissionAdmin(admin.ModelAdmin):
    list_display = ('id', 'task', 'user', 'status', 'submitted_at', 'updated_at')
    list_filter = ('status',)
    search_fields = ('task__title', 'user__username')
