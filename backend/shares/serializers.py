"""
Share 序列化器
"""

from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Share
from documents.models import Document
from files.models import File


class UserSimpleSerializer(serializers.ModelSerializer):
    """用户简要信息序列化器"""

    class Meta:
        model = User
        fields = ['id', 'username', 'first_name', 'last_name']


class ShareSerializer(serializers.ModelSerializer):
    """分享序列化器"""
    sharer_info = UserSimpleSerializer(source='sharer', read_only=True)
    sharee_info = UserSimpleSerializer(source='sharee', read_only=True)
    target_type = serializers.CharField(read_only=True)
    target_title = serializers.SerializerMethodField()

    class Meta:
        model = Share
        fields = [
            'id', 'document', 'file', 'sharer', 'sharee',
            'sharer_info', 'sharee_info',
            'permission', 'shared_at', 'expired_at',
            'is_active', 'message',
            'target_type', 'target_title'
        ]
        read_only_fields = ['sharer', 'shared_at', 'target_type']

    def get_target_title(self, obj):
        """获取分享目标的标题/名称"""
        if obj.document:
            return obj.document.title
        elif obj.file:
            return obj.file.original_name
        return ''

    def validate(self, attrs):
        """验证分享数据"""
        request = self.context.get('request')

        # 验证文档或文件至少有一个
        document = attrs.get('document')
        file = attrs.get('file')

        if not document and not file:
            raise serializers.ValidationError("必须指定文档或文件")

        # 验证被分享者
        sharee = attrs.get('sharee')
        if not sharee:
            raise serializers.ValidationError("必须指定被分享者")

        # 验证不能分享给自己
        if request and request.user == sharee:
            raise serializers.ValidationError("不能分享给自己")

        # 验证权限: 只能分享自己的文档/文件
        if document:
            if document.creator != request.user:
                raise serializers.ValidationError("只能分享自己的文档")
        elif file:
            if file.uploader != request.user:
                raise serializers.ValidationError("只能分享自己的文件")

        # 验证是否已存在相同的分享
        if self.instance is None:  # 创建时检查
            if Share.objects.filter(
                document=document,
                file=file,
                sharee=sharee,
                is_active=True
            ).exists():
                raise serializers.ValidationError("该资源已分享给该用户")

        return attrs

    def create(self, validated_data):
        """创建分享时自动设置分享者"""
        request = self.context.get('request')
        if request and hasattr(request, 'user'):
            validated_data['sharer'] = request.user
        return super().create(validated_data)


class ShareCreateSerializer(serializers.ModelSerializer):
    """创建分享专用序列化器"""

    class Meta:
        model = Share
        fields = ['document', 'file', 'sharee', 'permission', 'expired_at', 'message']
        extra_kwargs = {
            'document': {'required': False},
            'file': {'required': False},
            'message': {'required': False}
        }


class ShareListSerializer(serializers.ModelSerializer):
    """分享列表序列化器"""
    sharer_username = serializers.CharField(source='sharer.username', read_only=True)
    sharee_username = serializers.CharField(source='sharee.username', read_only=True)

    # 文档相关字段
    document_id = serializers.SerializerMethodField()
    document_title = serializers.SerializerMethodField()
    document_type = serializers.SerializerMethodField()

    # 文件相关字段
    file_id = serializers.SerializerMethodField()
    file_name = serializers.SerializerMethodField()
    file_size = serializers.SerializerMethodField()

    # 统一的目标字段
    target_type = serializers.SerializerMethodField()
    target_id = serializers.SerializerMethodField()
    target_title = serializers.SerializerMethodField()

    class Meta:
        model = Share
        fields = [
            'id', 'target_type', 'target_id', 'target_title',
            'sharer_username', 'sharee_username',
            'document_id', 'document_title', 'document_type',
            'file_id', 'file_name', 'file_size',
            'permission', 'shared_at', 'expired_at',
            'is_active', 'is_expired'
        ]

    def get_target_type(self, obj):
        """获取目标类型"""
        if obj.document:
            return 'document'
        elif obj.file:
            return 'file'
        return ''

    def get_target_id(self, obj):
        """获取目标ID"""
        if obj.document:
            return obj.document.id
        elif obj.file:
            return obj.file.id
        return None

    def get_target_title(self, obj):
        """获取目标标题"""
        if obj.document:
            return obj.document.title
        elif obj.file:
            return obj.file.original_name
        return ''

    def get_document_id(self, obj):
        if obj.document:
            return obj.document.id
        return None

    def get_document_title(self, obj):
        if obj.document:
            return obj.document.title
        return ''

    def get_document_type(self, obj):
        if obj.document:
            return obj.document.type
        return ''

    def get_file_id(self, obj):
        if obj.file:
            return obj.file.id
        return None

    def get_file_name(self, obj):
        if obj.file:
            return obj.file.original_name
        return ''

    def get_file_size(self, obj):
        if obj.file:
            return obj.file.size
        return 0
