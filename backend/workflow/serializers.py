from django.contrib.auth.models import User
from django.core.files.base import ContentFile
from django.db import transaction
from django.core.exceptions import ObjectDoesNotExist
from django.utils import timezone
from rest_framework import serializers

from accounts.models import Department, Organization
from .models import DistributionTask, Submission, TaskAssignment, Template


class TemplateSerializer(serializers.ModelSerializer):
    created_by_username = serializers.CharField(source='created_by.username', read_only=True)

    class Meta:
        model = Template
        fields = [
            'id',
            'name',
            'category',
            'description',
            'file',
            'editable_cells',
            'version',
            'is_active',
            'source_template',
            'created_by',
            'created_by_username',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'created_by', 'created_at', 'updated_at', 'version']


class DistributionTaskSerializer(serializers.ModelSerializer):
    created_by_username = serializers.CharField(source='created_by.username', read_only=True)
    template_name = serializers.CharField(source='template.name', read_only=True)
    template_version = serializers.IntegerField(read_only=True)
    template_snapshot_file = serializers.FileField(read_only=True)
    target_organizations = serializers.PrimaryKeyRelatedField(
        queryset=Organization.objects.filter(is_active=True), many=True, required=False
    )
    target_departments = serializers.PrimaryKeyRelatedField(
        queryset=Department.objects.filter(is_active=True), many=True, required=False
    )
    target_users = serializers.PrimaryKeyRelatedField(queryset=User.objects.filter(is_active=True), many=True, required=False)

    class Meta:
        model = DistributionTask
        fields = [
            'id',
            'title',
            'description',
            'template',
            'template_name',
            'created_by',
            'created_by_username',
            'template_version',
            'template_snapshot_file',
            'deadline',
            'status',
            'aggregation_rules',
            'target_organizations',
            'target_departments',
            'target_users',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'created_by', 'created_at', 'updated_at']

    def validate(self, attrs):
        if self.instance is None:
            has_any_target = any(
                attrs.get(field)
                for field in ('target_organizations', 'target_departments', 'target_users')
            )
            if not has_any_target:
                raise serializers.ValidationError('至少选择一个分发对象（组织/部门/用户）')
        return attrs

    @transaction.atomic
    def create(self, validated_data):
        organizations = validated_data.pop('target_organizations', [])
        departments = validated_data.pop('target_departments', [])
        users = validated_data.pop('target_users', [])

        template = validated_data['template']
        task = DistributionTask.objects.create(template_version=template.version, **validated_data)
        if template.file:
            template.file.open('rb')
            try:
                content = template.file.read()
            finally:
                template.file.close()
            filename = template.file.name.split('/')[-1]
            task.template_snapshot_file.save(filename, ContentFile(content), save=True)

        task.target_organizations.set(organizations)
        task.target_departments.set(departments)
        task.target_users.set(users)
        self._build_assignments(task)
        return task

    def _build_assignments(self, task):
        user_ids = set(task.target_users.values_list('id', flat=True))

        if task.target_organizations.exists():
            org_user_ids = User.objects.filter(
                profile__organization__in=task.target_organizations.all(),
                is_active=True,
            ).values_list('id', flat=True)
            user_ids.update(org_user_ids)

        if task.target_departments.exists():
            dept_user_ids = User.objects.filter(
                profile__department__in=task.target_departments.all(),
                is_active=True,
            ).values_list('id', flat=True)
            user_ids.update(dept_user_ids)

        if not user_ids:
            return

        profiles = User.objects.filter(id__in=user_ids).select_related('profile__organization', 'profile__department')
        assignments = []
        now = timezone.now()
        for user in profiles:
            try:
                profile = user.profile
            except ObjectDoesNotExist:
                profile = None
            assignments.append(
                TaskAssignment(
                    task=task,
                    assignee=user,
                    organization=getattr(profile, 'organization', None),
                    department=getattr(profile, 'department', None),
                    started_at=now if task.status != 'draft' else None,
                )
            )

        TaskAssignment.objects.bulk_create(assignments, ignore_conflicts=True)


class TaskAssignmentSerializer(serializers.ModelSerializer):
    task_title = serializers.CharField(source='task.title', read_only=True)
    template_id = serializers.IntegerField(source='task.template_id', read_only=True)
    template_name = serializers.CharField(source='task.template.name', read_only=True)
    task_deadline = serializers.DateTimeField(source='task.deadline', read_only=True)
    assignee_username = serializers.CharField(source='assignee.username', read_only=True)

    class Meta:
        model = TaskAssignment
        fields = [
            'id',
            'task',
            'task_title',
            'template_id',
            'template_name',
            'task_deadline',
            'assignee',
            'assignee_username',
            'organization',
            'department',
            'status',
            'started_at',
            'submitted_at',
            'returned_reason',
            'created_at',
            'updated_at',
        ]


class SubmissionSerializer(serializers.ModelSerializer):
    task_title = serializers.CharField(source='task.title', read_only=True)
    user_username = serializers.CharField(source='user.username', read_only=True)
    assignment_status = serializers.CharField(source='assignment.status', read_only=True)

    class Meta:
        model = Submission
        fields = [
            'id',
            'assignment',
            'task',
            'task_title',
            'user',
            'user_username',
            'organization',
            'file',
            'extracted_data',
            'status',
            'assignment_status',
            'submitted_at',
            'returned_reason',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'task', 'user', 'organization', 'submitted_at', 'created_at', 'updated_at']
        extra_kwargs = {
            'assignment': {'validators': []},
        }

    def validate_assignment(self, value):
        request = self.context['request']
        if value.assignee != request.user:
            raise serializers.ValidationError('只能提交自己的任务')
        if value.status in ('approved', 'expired'):
            raise serializers.ValidationError('当前任务实例状态不可提交')
        return value

    @transaction.atomic
    def create(self, validated_data):
        assignment = validated_data['assignment']
        submission, created = Submission.objects.get_or_create(
            assignment=assignment,
            defaults={
                'task': assignment.task,
                'user': assignment.assignee,
                'organization': assignment.organization,
                'extracted_data': validated_data.get('extracted_data', {}),
                'file': validated_data.get('file'),
                'status': 'draft',
            },
        )

        if not created:
            if submission.status not in ('draft', 'returned', 'withdrawn'):
                raise serializers.ValidationError('当前填报状态不可重新编辑')
            submission.extracted_data = validated_data.get('extracted_data', submission.extracted_data)
            if validated_data.get('file') is not None:
                submission.file = validated_data.get('file')
            if submission.status in ('returned', 'withdrawn'):
                submission.transition_to('draft')
            submission.save()

        if assignment.status != 'draft':
            assignment.transition_to('draft')
            assignment.save()
        return submission
