import os

from django.contrib.auth.models import User
from django.db import models
from django.utils import timezone

from accounts.models import Department, Organization


def template_upload_to(instance, filename):
    created_at = instance.created_at or timezone.now()
    return os.path.join('templates', instance.created_by.username, created_at.strftime('%Y/%m'), filename)


def submission_upload_to(instance, filename):
    created_at = instance.created_at or timezone.now()
    return os.path.join(
        'submissions',
        f'task_{instance.task_id}',
        instance.user.username,
        created_at.strftime('%Y/%m'),
        filename,
    )


def task_template_snapshot_upload_to(instance, filename):
    created_at = instance.created_at or timezone.now()
    return os.path.join('task_templates', f'task_{instance.id or "new"}', created_at.strftime('%Y/%m'), filename)


class Template(models.Model):
    """可分发的模板定义"""

    name = models.CharField(max_length=255, verbose_name='模板名称')
    category = models.CharField(max_length=100, blank=True, verbose_name='分类')
    description = models.TextField(blank=True, verbose_name='描述')
    file = models.FileField(upload_to=template_upload_to, verbose_name='模板文件')
    editable_cells = models.JSONField(default=list, blank=True, verbose_name='可填单元格配置')
    version = models.PositiveIntegerField(default=1, verbose_name='版本')
    is_active = models.BooleanField(default=True, verbose_name='是否启用')
    source_template = models.ForeignKey(
        'self',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='derived_versions',
        verbose_name='来源模板',
    )
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_templates', verbose_name='创建者')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    class Meta:
        db_table = 'workflow_template'
        ordering = ['-updated_at']
        indexes = [
            models.Index(fields=['is_active']),
            models.Index(fields=['name']),
            models.Index(fields=['created_by', '-created_at']),
        ]

    def __str__(self):
        return f'{self.name} v{self.version}'


class DistributionTask(models.Model):
    """模板分发任务"""

    STATUS_CHOICES = [
        ('draft', '草稿'),
        ('active', '进行中'),
        ('closed', '已关闭'),
        ('completed', '已完成'),
    ]

    title = models.CharField(max_length=255, verbose_name='任务标题')
    description = models.TextField(blank=True, verbose_name='任务说明')
    template = models.ForeignKey(Template, on_delete=models.PROTECT, related_name='tasks', verbose_name='模板')
    template_version = models.PositiveIntegerField(default=1, verbose_name='模板版本快照')
    template_snapshot_file = models.FileField(
        upload_to=task_template_snapshot_upload_to,
        null=True,
        blank=True,
        verbose_name='模板文件快照',
    )
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_tasks', verbose_name='创建人')
    deadline = models.DateTimeField(null=True, blank=True, verbose_name='截止时间')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active', verbose_name='任务状态')
    aggregation_rules = models.JSONField(default=dict, blank=True, verbose_name='汇总规则')
    target_organizations = models.ManyToManyField(
        Organization, blank=True, related_name='distribution_tasks', verbose_name='目标组织'
    )
    target_departments = models.ManyToManyField(
        Department, blank=True, related_name='distribution_tasks', verbose_name='目标部门'
    )
    target_users = models.ManyToManyField(User, blank=True, related_name='assigned_distribution_tasks', verbose_name='目标用户')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    class Meta:
        db_table = 'workflow_distribution_task'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['status']),
            models.Index(fields=['deadline']),
            models.Index(fields=['created_by', '-created_at']),
        ]

    def __str__(self):
        return self.title


class TaskAssignment(models.Model):
    """任务实例：每个接收者一条，便于跟踪状态"""

    STATUS_CHOICES = [
        ('pending', '未开始'),
        ('draft', '草稿'),
        ('submitted', '已上报'),
        ('returned', '已退回'),
        ('approved', '已通过'),
        ('withdrawn', '已撤回'),
        ('expired', '已过期'),
    ]

    task = models.ForeignKey(DistributionTask, on_delete=models.CASCADE, related_name='assignments', verbose_name='任务')
    assignee = models.ForeignKey(User, on_delete=models.CASCADE, related_name='task_assignments', verbose_name='接收人')
    organization = models.ForeignKey(
        Organization, null=True, blank=True, on_delete=models.SET_NULL, related_name='task_assignments', verbose_name='组织'
    )
    department = models.ForeignKey(
        Department, null=True, blank=True, on_delete=models.SET_NULL, related_name='task_assignments', verbose_name='部门'
    )
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', verbose_name='状态')
    started_at = models.DateTimeField(null=True, blank=True, verbose_name='开始时间')
    submitted_at = models.DateTimeField(null=True, blank=True, verbose_name='上报时间')
    returned_reason = models.TextField(blank=True, verbose_name='退回原因')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    class Meta:
        db_table = 'workflow_task_assignment'
        ordering = ['-created_at']
        constraints = [
            models.UniqueConstraint(fields=['task', 'assignee'], name='uniq_task_assignee_assignment'),
        ]
        indexes = [
            models.Index(fields=['status']),
            models.Index(fields=['assignee', '-created_at']),
            models.Index(fields=['task', 'status']),
        ]

    def __str__(self):
        return f'{self.task.title} -> {self.assignee.username}'

    ALLOWED_TRANSITIONS = {
        'pending': {'draft', 'submitted', 'expired'},
        'draft': {'submitted', 'expired'},
        'submitted': {'returned', 'approved', 'withdrawn'},
        'returned': {'draft', 'submitted', 'expired'},
        'withdrawn': {'draft', 'submitted', 'expired'},
        'approved': set(),
        'expired': set(),
    }

    def can_transition_to(self, next_status):
        return next_status in self.ALLOWED_TRANSITIONS.get(self.status, set())

    def transition_to(self, next_status, reason=''):
        if not self.can_transition_to(next_status):
            raise ValueError(f'状态不允许从 {self.status} 变更为 {next_status}')

        self.status = next_status
        if next_status in ('submitted', 'approved'):
            self.submitted_at = timezone.now()
            self.returned_reason = ''
        elif next_status == 'returned':
            self.returned_reason = reason
        elif next_status == 'draft':
            self.started_at = self.started_at or timezone.now()
            self.returned_reason = ''
        elif next_status in ('withdrawn', 'expired'):
            self.returned_reason = ''


class Submission(models.Model):
    """任务填报记录"""

    STATUS_CHOICES = [
        ('draft', '草稿'),
        ('submitted', '已上报'),
        ('returned', '已退回'),
        ('withdrawn', '已撤回'),
        ('approved', '已通过'),
    ]

    assignment = models.OneToOneField(TaskAssignment, on_delete=models.CASCADE, related_name='submission', verbose_name='任务实例')
    task = models.ForeignKey(DistributionTask, on_delete=models.CASCADE, related_name='submissions', verbose_name='任务')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='submissions', verbose_name='填报人')
    organization = models.ForeignKey(
        Organization, null=True, blank=True, on_delete=models.SET_NULL, related_name='submissions', verbose_name='组织'
    )
    file = models.FileField(upload_to=submission_upload_to, null=True, blank=True, verbose_name='填报文件')
    extracted_data = models.JSONField(default=dict, blank=True, verbose_name='提取数据')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft', verbose_name='状态')
    submitted_at = models.DateTimeField(null=True, blank=True, verbose_name='上报时间')
    returned_reason = models.TextField(blank=True, verbose_name='退回原因')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    class Meta:
        db_table = 'workflow_submission'
        ordering = ['-updated_at']
        indexes = [
            models.Index(fields=['status']),
            models.Index(fields=['task', 'status']),
            models.Index(fields=['user', '-updated_at']),
        ]

    def __str__(self):
        return f'{self.task.title} / {self.user.username} / {self.status}'

    ALLOWED_TRANSITIONS = {
        'draft': {'submitted'},
        'submitted': {'withdrawn', 'returned', 'approved'},
        'returned': {'draft', 'submitted'},
        'withdrawn': {'draft', 'submitted'},
        'approved': {'returned'},
    }

    def can_transition_to(self, next_status):
        return next_status in self.ALLOWED_TRANSITIONS.get(self.status, set())

    def transition_to(self, next_status, reason=''):
        if not self.can_transition_to(next_status):
            raise ValueError(f'状态不允许从 {self.status} 变更为 {next_status}')

        self.status = next_status
        if next_status in ('submitted', 'approved'):
            self.submitted_at = timezone.now()
            self.returned_reason = ''
        elif next_status == 'returned':
            self.returned_reason = reason
        elif next_status in ('draft', 'withdrawn'):
            self.returned_reason = ''
