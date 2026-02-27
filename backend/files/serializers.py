"""
文件序列化器
"""

from rest_framework import serializers
from .models import File


class FileSerializer(serializers.ModelSerializer):
    """文件序列化器"""

    file_url = serializers.ReadOnlyField()
    file_size_display = serializers.ReadOnlyField()
    file_type = serializers.ReadOnlyField()
    uploader_name = serializers.CharField(source='uploader.username', read_only=True)

    # 兼容不同前端字段命名
    name = serializers.CharField(source='original_name', read_only=True)
    creator = serializers.IntegerField(source='uploader_id', read_only=True)
    creator_username = serializers.CharField(source='uploader.username', read_only=True)

    class Meta:
        model = File
        fields = [
            'id',
            'file',
            'file_url',
            'original_name',
            'name',
            'size',
            'file_size_display',
            'mime_type',
            'file_type',
            'uploader',
            'uploader_name',
            'creator',
            'creator_username',
            'created_at',
            'updated_at',
            'is_deleted',
        ]
        read_only_fields = [
            'uploader',
            'original_name',
            'size',
            'mime_type',
            'created_at',
            'updated_at',
            'file_url',
            'is_deleted',
        ]

    def validate(self, attrs):
        if self.instance is None and 'file' not in attrs:
            raise serializers.ValidationError('请上传文件')
        return attrs

    def create(self, validated_data):
        request = self.context.get('request')
        file_obj = validated_data['file']
        validated_data['uploader'] = request.user
        validated_data['original_name'] = file_obj.name
        validated_data['size'] = file_obj.size
        validated_data['mime_type'] = getattr(file_obj, 'content_type', '') or 'application/octet-stream'
        return super().create(validated_data)
