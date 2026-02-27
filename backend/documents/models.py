"""
Document 模型 - 支持 OnlyOffice 在线编辑

文档类型:
- word: Word 文档 (.docx, .doc, .odt, .rtf, .txt)
- cell: Excel 表格 (.xlsx, .xls, .ods)
- slide: PPT 演示 (.pptx, .ppt, .odp)
"""

import os
from datetime import datetime
from django.db import models
from django.contrib.auth.models import User
from django.core.validators import FileExtensionValidator


def document_upload_to(instance, filename):
    """动态生成文档上传路径"""
    ext = os.path.splitext(filename)[1].lower()
    return os.path.join(
        'documents',
        instance.creator.username,
        instance.created_at.strftime('%Y/%m'),
        filename
    )


class Document(models.Model):
    """文档模型"""

    DOCUMENT_TYPE_CHOICES = [
        ('word', 'Word文档'),
        ('cell', 'Excel表格'),
        ('slide', 'PPT演示'),
    ]

    # 基本信息
    title = models.CharField(max_length=255, default='未命名文档', verbose_name='标题')
    type = models.CharField(
        max_length=20,
        choices=DOCUMENT_TYPE_CHOICES,
        default='word',
        verbose_name='类型'
    )

    # 文件存储 (用于 OnlyOffice)
    file = models.FileField(
        upload_to=document_upload_to,
        validators=[FileExtensionValidator(
            allowed_extensions=[
                # Word 文档
                'docx', 'doc', 'odt', 'rtf', 'txt', 'html', 'htm',
                # Excel 表格
                'xlsx', 'xls', 'ods', 'csv',
                # PPT 演示
                'pptx', 'ppt', 'odp'
            ]
        )],
        verbose_name='文档文件',
        null=True,
        blank=True
    )

    # OnlyOffice 相关字段
    file_key = models.CharField(
        max_length=255,
        blank=True,
        verbose_name='文档唯一标识'
    )

    # 编辑状态
    is_locked = models.BooleanField(default=False, verbose_name='是否锁定')
    locked_by = models.ForeignKey(
        User,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='locked_documents',
        verbose_name='锁定用户'
    )
    locked_at = models.DateTimeField(null=True, blank=True, verbose_name='锁定时间')

    # 协同编辑
    session_id = models.CharField(
        max_length=255,
        blank=True,
        verbose_name='编辑会话ID'
    )

    # 关联信息
    creator = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='documents',
        verbose_name='创建者'
    )

    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    version = models.IntegerField(default=1, verbose_name='版本号')
    is_deleted = models.BooleanField(default=False, verbose_name='是否删除')
    deleted_at = models.DateTimeField(null=True, blank=True, verbose_name='删除时间')

    class Meta:
        db_table = 'document'
        verbose_name = '文档'
        verbose_name_plural = '文档'
        ordering = ['-updated_at']
        indexes = [
            models.Index(fields=['creator', '-updated_at']),
            models.Index(fields=['type']),
            models.Index(fields=['is_deleted']),
            models.Index(fields=['file_key']),
        ]

    def __str__(self):
        return f'{self.title} ({self.get_type_display()})'

    @property
    def file_url(self):
        """获取文档的完整访问URL"""
        if self.file:
            return self.file.url
        return None

    @property
    def file_extension(self):
        """获取文件扩展名"""
        if self.file:
            return os.path.splitext(self.file.name)[1].lower().replace('.', '')
        return None

    @property
    def file_type(self):
        """根据扩展名返回文件类型 (用于 OnlyOffice)"""
        ext = self.file_extension
        if not ext:
            return 'docx'

        # 文档类型映射
        doc_exts = ['docx', 'doc', 'odt', 'rtf', 'txt', 'html', 'htm']
        cell_exts = ['xlsx', 'xls', 'ods', 'csv']
        slide_exts = ['pptx', 'ppt', 'odp']

        if ext in cell_exts:
            return 'xlsx'
        elif ext in slide_exts:
            return 'pptx'
        else:
            return 'docx'

    def save(self, *args, **kwargs):
        """
        保存文档。

        仅当文件本身发生变化时才自动升级 version 并刷新 file_key，
        避免普通字段保存触发 OnlyOffice 会话版本变更。
        """
        update_fields = kwargs.get('update_fields')
        is_create = self._state.adding

        if is_create:
            # 先保存拿到主键，再补充可追踪的 file_key
            if not self.file_key:
                self.file_key = f"new_{int(datetime.now().timestamp())}"
            super().save(*args, **kwargs)
            if self.file_key.startswith('new_'):
                self.file_key = f"{self.id}_{self.version}_{int(datetime.now().timestamp())}"
                super().save(update_fields=['file_key'])
            return

        # 判断是否是文件更新
        if update_fields is not None:
            should_bump_version = 'file' in set(update_fields)
        else:
            old = Document.objects.filter(pk=self.pk).only('file').first()
            old_file_name = old.file.name if old and old.file else ''
            new_file_name = self.file.name if self.file else ''
            should_bump_version = old_file_name != new_file_name

        if should_bump_version:
            self.version += 1
            self.file_key = f"{self.id}_{self.version}_{int(datetime.now().timestamp())}"
            if update_fields is not None:
                merged = set(update_fields) | {'version', 'file_key'}
                kwargs['update_fields'] = list(merged)

        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        """删除时同时删除文件"""
        if self.file:
            if os.path.isfile(self.file.path):
                os.remove(self.file.path)
        super().delete(*args, **kwargs)
