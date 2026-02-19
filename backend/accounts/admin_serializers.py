"""
管理后台序列化器
"""
from django.db import models
from rest_framework import serializers
from django.contrib.auth.models import User
from documents.models import Document
from files.models import File
from shares.models import Share


class AdminUserSerializer(serializers.ModelSerializer):
    """管理后台用户序列化器"""
    document_count = serializers.SerializerMethodField()
    file_count = serializers.SerializerMethodField()
    share_count = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            'id', 'username', 'email', 'first_name', 'last_name',
            'is_staff', 'is_active', 'date_joined',
            'document_count', 'file_count', 'share_count',
            'last_login'
        ]
        read_only_fields = ['date_joined', 'last_login']

    def get_document_count(self, obj):
        """获取用户创建的文档数量"""
        return Document.objects.filter(creator=obj, is_deleted=False).count()

    def get_file_count(self, obj):
        """获取用户上传的文件数量"""
        return File.objects.filter(uploader=obj, is_deleted=False).count()

    def get_share_count(self, obj):
        """获取用户的分享数量（分享出去的 + 收到的）"""
        return Share.objects.filter(
            models.Q(sharer=obj) | models.Q(sharee=obj),
            is_active=True
        ).count()


class AdminDocumentSerializer(serializers.ModelSerializer):
    """管理后台文档序列化器"""
    creator_name = serializers.CharField(source='creator.username', read_only=True)
    creator_email = serializers.CharField(source='creator.email', read_only=True)
    share_count = serializers.SerializerMethodField()

    class Meta:
        model = Document
        fields = [
            'id', 'title', 'type', 'creator', 'creator_name', 'creator_email',
            'created_at', 'updated_at', 'version', 'is_deleted',
            'share_count'
        ]

    def get_share_count(self, obj):
        """获取文档被分享的次数"""
        return obj.shares.filter(is_active=True).count()


class AdminFileSerializer(serializers.ModelSerializer):
    """管理后台文件序列化器"""
    uploader_name = serializers.CharField(source='uploader.username', read_only=True)
    uploader_email = serializers.CharField(source='uploader.email', read_only=True)
    share_count = serializers.SerializerMethodField()

    class Meta:
        model = File
        fields = [
            'id', 'original_name', 'size', 'mime_type',
            'uploader', 'uploader_name', 'uploader_email',
            'created_at', 'is_deleted',
            'share_count'
        ]

    def get_share_count(self, obj):
        """获取文件被分享的次数"""
        return obj.shares.filter(is_active=True).count()


class AdminStatisticsSerializer(serializers.Serializer):
    """统计信息序列化器"""
    user_total = serializers.IntegerField()
    user_active = serializers.IntegerField()
    document_total = serializers.IntegerField()
    file_total = serializers.IntegerField()
    share_total = serializers.IntegerField()
    storage_used = serializers.IntegerField()


class AdminUserUpdateSerializer(serializers.ModelSerializer):
    """管理后台用户更新序列化器"""

    class Meta:
        model = User
        fields = ['is_staff', 'is_active']

    def validate(self, attrs):
        """验证数据"""
        # 不能禁用或取消超级管理员的管理员权限
        if self.instance and self.instance.is_superuser:
            if 'is_staff' in attrs and not attrs['is_staff']:
                raise serializers.ValidationError("不能取消超级管理员的管理员权限")
            if 'is_active' in attrs and not attrs['is_active']:
                raise serializers.ValidationError("不能禁用超级管理员账号")
        return attrs
