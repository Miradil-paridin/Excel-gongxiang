"""
Share 模型

支持文档和文件的分享
"""

from django.db import models
from django.contrib.auth.models import User
from documents.models import Document
from files.models import File


class Share(models.Model):
    """分享模型"""

    PERMISSION_CHOICES = [
        ('read', '只读'),
        ('write', '可编辑'),
    ]

    # 分享的文档或文件 (二选一)
    document = models.ForeignKey(
        Document,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='shares',
        verbose_name='文档'
    )

    file = models.ForeignKey(
        File,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='shares',
        verbose_name='文件'
    )

    # 分享者
    sharer = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='shared_from',
        verbose_name='分享者'
    )

    # 被分享者
    sharee = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='shared_to',
        verbose_name='被分享者'
    )

    # 权限
    permission = models.CharField(
        max_length=20,
        choices=PERMISSION_CHOICES,
        default='read',
        verbose_name='权限'
    )

    # 分享时间
    shared_at = models.DateTimeField(auto_now_add=True, verbose_name='分享时间')

    # 过期时间 (可选)
    expired_at = models.DateTimeField(null=True, blank=True, verbose_name='过期时间')

    # 是否激活
    is_active = models.BooleanField(default=True, verbose_name='是否激活')

    # 分享留言 (可选)
    message = models.TextField(blank=True, verbose_name='留言')

    class Meta:
        db_table = 'share'
        verbose_name = '分享'
        verbose_name_plural = '分享'
        ordering = ['-shared_at']
        indexes = [
            models.Index(fields=['sharer', '-shared_at']),
            models.Index(fields=['sharee', '-shared_at']),
            models.Index(fields=['document']),
            models.Index(fields=['file']),
            models.Index(fields=['is_active']),
        ]
        constraints = [
            # 确保 document 和 file 至少有一个不为空
            models.CheckConstraint(
                check=models.Q(document__isnull=False) | models.Q(file__isnull=False),
                name='share_document_or_file_not_null'
            )
        ]

    def __str__(self):
        target = self.document.title if self.document else self.file.original_name
        return f'{self.sharer.username} 分享 {target} 给 {self.sharee.username}'

    def is_expired(self):
        """检查是否过期"""
        if not self.expired_at:
            return False
        from django.utils import timezone
        return timezone.now() > self.expired_at

    @property
    def target_type(self):
        """获取分享目标类型"""
        if self.document:
            return 'document'
        elif self.file:
            return 'file'
        return None

    @property
    def target(self):
        """获取分享目标对象"""
        return self.document or self.file
