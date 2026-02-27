from django.contrib.auth.models import User
from django.db import models


class Organization(models.Model):
    """单位/组织"""

    name = models.CharField(max_length=128, unique=True, verbose_name='单位名称')
    code = models.CharField(max_length=64, unique=True, verbose_name='单位编码')
    is_active = models.BooleanField(default=True, verbose_name='是否启用')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    class Meta:
        db_table = 'organization'
        verbose_name = '单位'
        verbose_name_plural = '单位'
        ordering = ['name']

    def __str__(self):
        return self.name


class Department(models.Model):
    """部门"""

    organization = models.ForeignKey(
        Organization,
        on_delete=models.CASCADE,
        related_name='departments',
        verbose_name='所属单位',
    )
    name = models.CharField(max_length=128, verbose_name='部门名称')
    code = models.CharField(max_length=64, verbose_name='部门编码')
    parent = models.ForeignKey(
        'self',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='children',
        verbose_name='上级部门',
    )
    is_active = models.BooleanField(default=True, verbose_name='是否启用')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    class Meta:
        db_table = 'department'
        verbose_name = '部门'
        verbose_name_plural = '部门'
        ordering = ['organization__name', 'name']
        constraints = [
            models.UniqueConstraint(fields=['organization', 'code'], name='uniq_department_org_code'),
            models.UniqueConstraint(fields=['organization', 'name'], name='uniq_department_org_name'),
        ]

    def __str__(self):
        return f'{self.organization.name} / {self.name}'


class UserProfile(models.Model):
    """用户扩展信息"""

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='profile',
        verbose_name='用户',
    )
    organization = models.ForeignKey(
        Organization,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='users',
        verbose_name='所属单位',
    )
    department = models.ForeignKey(
        Department,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='users',
        verbose_name='所属部门',
    )
    role_title = models.CharField(max_length=128, blank=True, verbose_name='岗位/角色')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    class Meta:
        db_table = 'user_profile'
        verbose_name = '用户扩展信息'
        verbose_name_plural = '用户扩展信息'

    def __str__(self):
        return f'{self.user.username} profile'
