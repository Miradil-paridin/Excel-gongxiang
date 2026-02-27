"""
文件模型
"""

import mimetypes
import os
from django.contrib.auth.models import User
from django.db import models
from django.utils import timezone


def file_upload_to(instance, filename):
    """动态生成上传路径"""
    created_at = instance.created_at or timezone.now()
    return os.path.join(
        'files',
        instance.uploader.username,
        created_at.strftime('%Y/%m'),
        filename,
    )


class File(models.Model):
    """文件模型"""

    file = models.FileField(upload_to=file_upload_to, verbose_name='文件')
    original_name = models.CharField(max_length=255, verbose_name='原文件名')
    size = models.BigIntegerField(default=0, verbose_name='文件大小(字节)')
    mime_type = models.CharField(max_length=255, blank=True, verbose_name='MIME类型')

    uploader = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='uploaded_files',
        verbose_name='上传者',
    )

    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')
    is_deleted = models.BooleanField(default=False, verbose_name='是否删除')
    deleted_at = models.DateTimeField(null=True, blank=True, verbose_name='删除时间')

    class Meta:
        db_table = 'file'
        verbose_name = '文件'
        verbose_name_plural = '文件'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['uploader', '-created_at']),
            models.Index(fields=['is_deleted']),
        ]

    def __str__(self):
        return self.original_name

    @property
    def file_url(self):
        if not self.file:
            return None
        return self.file.url

    @property
    def file_size_display(self):
        size = self.size or 0
        units = ['B', 'KB', 'MB', 'GB', 'TB']
        index = 0
        while size >= 1024 and index < len(units) - 1:
            size /= 1024
            index += 1
        return f'{size:.1f} {units[index]}'

    @property
    def file_type(self):
        if self.mime_type.startswith('image/'):
            return 'image'
        if 'sheet' in self.mime_type or 'excel' in self.mime_type or self.original_name.endswith(('.xlsx', '.xls', '.csv')):
            return 'spreadsheet'
        if 'presentation' in self.mime_type or self.original_name.endswith(('.ppt', '.pptx')):
            return 'presentation'
        if 'document' in self.mime_type or self.original_name.endswith(('.doc', '.docx', '.txt', '.pdf')):
            return 'document'
        if any(self.original_name.endswith(ext) for ext in ('.zip', '.rar', '.7z', '.tar', '.gz')):
            return 'archive'
        return 'file'

    def save(self, *args, **kwargs):
        if self.file:
            if not self.original_name:
                self.original_name = os.path.basename(self.file.name)
            if not self.size:
                self.size = self.file.size
            if not self.mime_type:
                self.mime_type = mimetypes.guess_type(self.original_name)[0] or 'application/octet-stream'
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        storage = self.file.storage if self.file else None
        file_name = self.file.name if self.file else None
        super().delete(*args, **kwargs)
        if storage and file_name:
            storage.delete(file_name)


class FileEditableDocument(models.Model):
    """记录用户对上传文件的一键编辑文档映射，避免重复创建文档"""

    file = models.ForeignKey(
        File,
        on_delete=models.CASCADE,
        related_name='editable_links',
        verbose_name='源文件',
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='file_editable_links',
        verbose_name='用户',
    )
    document = models.ForeignKey(
        'documents.Document',
        on_delete=models.CASCADE,
        related_name='file_source_links',
        verbose_name='在线文档',
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    class Meta:
        db_table = 'file_editable_document'
        verbose_name = '文件可编辑映射'
        verbose_name_plural = '文件可编辑映射'
        constraints = [
            models.UniqueConstraint(fields=['file', 'user'], name='uniq_file_user_editable_doc'),
        ]

    def __str__(self):
        return f'{self.user.username}: {self.file.original_name} -> {self.document_id}'
