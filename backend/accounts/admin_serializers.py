"""
管理后台序列化器
"""
from django.contrib.auth.models import Group, User
from django.db import models
from rest_framework import serializers

from documents.models import Document
from files.models import File
from shares.models import Share
from .models import Department, Organization, UserProfile


class AdminOrganizationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Organization
        fields = ['id', 'name', 'code', 'is_active', 'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at']


class AdminDepartmentSerializer(serializers.ModelSerializer):
    organization_name = serializers.CharField(source='organization.name', read_only=True)
    parent_name = serializers.CharField(source='parent.name', read_only=True)

    class Meta:
        model = Department
        fields = [
            'id',
            'name',
            'code',
            'organization',
            'organization_name',
            'parent',
            'parent_name',
            'is_active',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['created_at', 'updated_at']


class AdminGroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = Group
        fields = ['id', 'name']


class AdminUserSerializer(serializers.ModelSerializer):
    """管理后台用户序列化器"""

    document_count = serializers.SerializerMethodField()
    file_count = serializers.SerializerMethodField()
    share_count = serializers.SerializerMethodField()
    organization = serializers.SerializerMethodField()
    organization_name = serializers.SerializerMethodField()
    department = serializers.SerializerMethodField()
    department_name = serializers.SerializerMethodField()
    role_title = serializers.SerializerMethodField()
    groups = serializers.SerializerMethodField()
    group_ids = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            'id',
            'username',
            'email',
            'first_name',
            'last_name',
            'is_staff',
            'is_superuser',
            'is_active',
            'date_joined',
            'last_login',
            'document_count',
            'file_count',
            'share_count',
            'organization',
            'organization_name',
            'department',
            'department_name',
            'role_title',
            'groups',
            'group_ids',
        ]
        read_only_fields = ['date_joined', 'last_login']

    def _get_profile(self, obj):
        profile, _ = UserProfile.objects.get_or_create(user=obj)
        return profile

    def get_document_count(self, obj):
        return Document.objects.filter(creator=obj, is_deleted=False).count()

    def get_file_count(self, obj):
        return File.objects.filter(uploader=obj, is_deleted=False).count()

    def get_share_count(self, obj):
        return Share.objects.filter(
            models.Q(sharer=obj) | models.Q(sharee=obj),
            is_active=True,
        ).count()

    def get_organization(self, obj):
        return self._get_profile(obj).organization_id

    def get_organization_name(self, obj):
        org = self._get_profile(obj).organization
        return org.name if org else ''

    def get_department(self, obj):
        return self._get_profile(obj).department_id

    def get_department_name(self, obj):
        dept = self._get_profile(obj).department
        return dept.name if dept else ''

    def get_role_title(self, obj):
        return self._get_profile(obj).role_title

    def get_groups(self, obj):
        return list(obj.groups.values_list('name', flat=True))

    def get_group_ids(self, obj):
        return list(obj.groups.values_list('id', flat=True))


class AdminUserCreateSerializer(serializers.ModelSerializer):
    """管理员创建用户"""

    password = serializers.CharField(write_only=True, min_length=8)
    organization = serializers.IntegerField(required=False, allow_null=True)
    department = serializers.IntegerField(required=False, allow_null=True)
    role_title = serializers.CharField(required=False, allow_blank=True)
    group_ids = serializers.ListField(
        child=serializers.IntegerField(),
        required=False,
        allow_empty=True,
    )

    class Meta:
        model = User
        fields = [
            'username',
            'email',
            'first_name',
            'last_name',
            'password',
            'is_staff',
            'is_active',
            'organization',
            'department',
            'role_title',
            'group_ids',
        ]

    def validate_username(self, value):
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError('用户名已存在')
        return value

    def validate_email(self, value):
        if value and User.objects.filter(email=value).exists():
            raise serializers.ValidationError('邮箱已存在')
        return value

    def validate(self, attrs):
        request = self.context.get('request')
        org_id = attrs.get('organization')
        dept_id = attrs.get('department')
        group_ids = attrs.get('group_ids') or []

        if request and not request.user.is_superuser:
            if attrs.get('is_staff'):
                raise serializers.ValidationError({'is_staff': '仅超级管理员可创建管理员账号'})
            if group_ids:
                raise serializers.ValidationError({'group_ids': '仅超级管理员可分配用户组'})

        if dept_id:
            try:
                dept = Department.objects.select_related('organization').get(id=dept_id)
            except Department.DoesNotExist:
                raise serializers.ValidationError({'department': '部门不存在'})
            if org_id and dept.organization_id != org_id:
                raise serializers.ValidationError({'department': '部门不属于指定单位'})
            if not org_id:
                attrs['organization'] = dept.organization_id

        return attrs

    def create(self, validated_data):
        org_id = validated_data.pop('organization', None)
        dept_id = validated_data.pop('department', None)
        role_title = validated_data.pop('role_title', '')
        group_ids = validated_data.pop('group_ids', [])
        password = validated_data.pop('password')

        user = User.objects.create_user(password=password, **validated_data)

        profile, _ = UserProfile.objects.get_or_create(user=user)
        profile.organization_id = org_id
        profile.department_id = dept_id
        profile.role_title = role_title
        profile.save()

        if group_ids:
            groups = Group.objects.filter(id__in=group_ids)
            user.groups.set(groups)

        return user


class AdminUserUpdateSerializer(serializers.ModelSerializer):
    """管理后台用户更新序列化器"""

    organization = serializers.IntegerField(required=False, allow_null=True)
    department = serializers.IntegerField(required=False, allow_null=True)
    role_title = serializers.CharField(required=False, allow_blank=True)
    group_ids = serializers.ListField(
        child=serializers.IntegerField(),
        required=False,
        allow_empty=True,
    )
    password = serializers.CharField(write_only=True, required=False, min_length=8)

    class Meta:
        model = User
        fields = [
            'email',
            'first_name',
            'last_name',
            'is_staff',
            'is_active',
            'organization',
            'department',
            'role_title',
            'group_ids',
            'password',
        ]

    def validate(self, attrs):
        request = self.context.get('request')
        if self.instance and self.instance.is_superuser:
            if attrs.get('is_staff') is False:
                raise serializers.ValidationError('不能取消超级管理员的管理员权限')
            if attrs.get('is_active') is False:
                raise serializers.ValidationError('不能禁用超级管理员账号')

        if request and not request.user.is_superuser:
            if 'is_staff' in attrs:
                raise serializers.ValidationError({'is_staff': '仅超级管理员可调整管理员权限'})
            if 'group_ids' in attrs:
                raise serializers.ValidationError({'group_ids': '仅超级管理员可调整用户组'})
            if self.instance and self.instance.is_staff:
                raise serializers.ValidationError('仅超级管理员可修改管理员账号')

        org_id = attrs.get('organization', serializers.empty)
        dept_id = attrs.get('department', serializers.empty)

        final_org_id = self.instance.profile.organization_id if hasattr(self.instance, 'profile') else None
        if org_id is not serializers.empty:
            final_org_id = org_id

        if dept_id not in (serializers.empty, None):
            try:
                dept = Department.objects.select_related('organization').get(id=dept_id)
            except Department.DoesNotExist:
                raise serializers.ValidationError({'department': '部门不存在'})

            if final_org_id and dept.organization_id != final_org_id:
                raise serializers.ValidationError({'department': '部门不属于指定单位'})

            if final_org_id is None:
                attrs['organization'] = dept.organization_id

        return attrs

    def update(self, instance, validated_data):
        org_id = validated_data.pop('organization', serializers.empty)
        dept_id = validated_data.pop('department', serializers.empty)
        role_title = validated_data.pop('role_title', serializers.empty)
        group_ids = validated_data.pop('group_ids', serializers.empty)
        password = validated_data.pop('password', None)

        for key, value in validated_data.items():
            setattr(instance, key, value)

        if password:
            instance.set_password(password)

        instance.save()

        profile, _ = UserProfile.objects.get_or_create(user=instance)
        if org_id is not serializers.empty:
            profile.organization_id = org_id
        if dept_id is not serializers.empty:
            profile.department_id = dept_id
        if role_title is not serializers.empty:
            profile.role_title = role_title
        profile.save()

        if group_ids is not serializers.empty:
            groups = Group.objects.filter(id__in=group_ids)
            instance.groups.set(groups)

        return instance


class AdminDocumentSerializer(serializers.ModelSerializer):
    creator_name = serializers.CharField(source='creator.username', read_only=True)
    creator_email = serializers.CharField(source='creator.email', read_only=True)
    share_count = serializers.SerializerMethodField()

    class Meta:
        model = Document
        fields = [
            'id',
            'title',
            'type',
            'creator',
            'creator_name',
            'creator_email',
            'created_at',
            'updated_at',
            'version',
            'is_deleted',
            'share_count',
        ]

    def get_share_count(self, obj):
        return obj.shares.filter(is_active=True).count()


class AdminFileSerializer(serializers.ModelSerializer):
    uploader_name = serializers.CharField(source='uploader.username', read_only=True)
    uploader_email = serializers.CharField(source='uploader.email', read_only=True)
    share_count = serializers.SerializerMethodField()

    class Meta:
        model = File
        fields = [
            'id',
            'original_name',
            'size',
            'mime_type',
            'uploader',
            'uploader_name',
            'uploader_email',
            'created_at',
            'is_deleted',
            'share_count',
        ]

    def get_share_count(self, obj):
        return obj.shares.filter(is_active=True).count()


class AdminStatisticsSerializer(serializers.Serializer):
    user_total = serializers.IntegerField()
    user_active = serializers.IntegerField()
    document_total = serializers.IntegerField()
    file_total = serializers.IntegerField()
    share_total = serializers.IntegerField()
    storage_used = serializers.IntegerField()
