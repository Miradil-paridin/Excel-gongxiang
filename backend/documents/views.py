"""
Document 视图
"""

import uuid
from datetime import datetime, timedelta
from rest_framework import status, generics, filters
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from django.conf import settings
from django.db.models import Q
from .models import Document
from .serializers import DocumentSerializer, DocumentListSerializer
from accounts.permissions import IsOwnerOrAdmin
from shares.models import Share


class DocumentListCreateView(generics.ListCreateAPIView):
    """文档列表和创建视图"""
    serializer_class = DocumentListSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['type', 'is_deleted']
    search_fields = ['title']
    ordering_fields = ['created_at', 'updated_at', 'title']
    ordering = ['-updated_at']

    def get_queryset(self):
        """获取当前用户自己的文档 + 被分享的文档"""
        user = self.request.user

        # 获取用户自己的文档
        own_docs = Document.objects.filter(creator=user, is_deleted=False)

        # 获取被分享的文档
        shared_docs = Document.objects.filter(
            shares__sharee=user,
            shares__is_active=True,
            is_deleted=False
        )

        # 合并查询结果
        return (own_docs | shared_docs).distinct().order_by('-updated_at')

    def create(self, request, *args, **kwargs):
        """创建文档"""
        serializer = DocumentSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)

        headers = self.get_success_headers(serializer.data)
        # 返回完整信息
        return Response({
            'code': 0,
            'message': '文档创建成功',
            'data': serializer.data
        }, status=status.HTTP_201_CREATED, headers=headers)

    def list(self, request, *args, **kwargs):
        """获取文档列表"""
        queryset = self.filter_queryset(self.get_queryset())

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            response = self.get_paginated_response(serializer.data)
            return Response({
                'code': 0,
                'message': 'success',
                'data': response.data['results'],
                'count': response.data['count'],
                'next': response.data['next'],
                'previous': response.data['previous']
            })

        serializer = self.get_serializer(queryset, many=True)
        return Response({
            'code': 0,
            'message': 'success',
            'data': serializer.data
        })


class DocumentDetailView(generics.RetrieveUpdateDestroyAPIView):
    """文档详情、更新、删除视图"""
    serializer_class = DocumentSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """允许访问自己的文档和被分享的文档"""
        user = self.request.user
        # 获取用户自己的文档
        own_docs = Document.objects.filter(creator=user, is_deleted=False)
        # 获取被分享的文档
        shared_docs = Document.objects.filter(
            shares__sharee=user,
            shares__is_active=True,
            is_deleted=False
        )
        return (own_docs | shared_docs).distinct()

    def update(self, request, *args, **kwargs):
        """更新文档"""
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        return Response({
            'code': 0,
            'message': '文档更新成功',
            'data': serializer.data
        })

    def destroy(self, request, *args, **kwargs):
        """软删除文档"""
        instance = self.get_object()
        instance.is_deleted = True
        instance.save()

        return Response({
            'code': 0,
            'message': '文档已删除'
        }, status=status.HTTP_200_OK)


class DocumentRestoreView(generics.GenericAPIView):
    """恢复已删除文档"""
    permission_classes = [IsAuthenticated, IsOwnerOrAdmin]

    def get_queryset(self):
        return Document.objects.filter(creator=self.request.user)

    def post(self, request, pk):
        """恢复文档"""
        try:
            document = self.get_queryset().get(pk=pk, is_deleted=True)
            document.is_deleted = False
            document.deleted_at = None
            document.save()

            return Response({
                'code': 0,
                'message': '文档已恢复'
            })
        except Document.DoesNotExist:
            return Response({
                'code': 1,
                'message': '文档不存在或未被删除'
            }, status=status.HTTP_404_NOT_FOUND)


class DocumentEditorConfigView(generics.GenericAPIView):
    """返回 OnlyOffice 编辑器配置"""
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Document.objects.filter(is_deleted=False)

    def get(self, request, pk):
        """获取文档编辑器配置"""
        try:
            document = self.get_queryset().get(pk=pk)
        except Document.DoesNotExist:
            return Response({
                'code': 1,
                'message': '文档不存在'
            }, status=status.HTTP_404_NOT_FOUND)

        # 检查权限：创建者或拥有写权限的分享对象
        can_edit = document.creator == request.user

        if not can_edit:
            # 检查是否被分享且有写权限
            share = Share.objects.filter(
                document=document,
                sharee=request.user,
                is_active=True,
                permission='write'
            ).first()
            can_edit = share is not None

        # 生成文档 key（使用 UUID 保证唯一性）
        if not document.file_key:
            document.file_key = f"{document.id}_{int(datetime.now().timestamp())}"
            document.save(update_fields=['file_key'])

        # 获取文档 URL
        document_url = None
        if document.file:
            # 使用配置的 OnlyOffice 访问地址
            doc_url_base = getattr(settings, 'ONLYOFFICE_DOCUMENT_URL', None)
            if doc_url_base:
                document_url = f"{doc_url_base}{settings.MEDIA_URL}{document.file.name}"
            else:
                # 构建完整的文档访问 URL
                protocol = 'https' if request.is_secure() else 'http'
                host = request.get_host()
                document_url = f"{protocol}://{host}{settings.MEDIA_URL}{document.file.name}"

        # 构建 OnlyOffice 配置
        config = {
            'document': {
                'fileType': document.file_extension or 'docx',
                'key': document.file_key,
                'title': document.title,
                'url': document_url,
            },
            'documentType': document.type,  # word, cell, slide
            'editorConfig': {
                'mode': 'edit' if can_edit else 'view',
                'lang': 'zh-CN',
                'user': {
                    'id': str(request.user.id),
                    'name': request.user.username,
                },
                'callbackUrl': f"{settings.ONLYOFFICE_DOCUMENT_URL}/api/documents/callback/",
            }
        }

        # 如果启用了 JWT
        if settings.ONLYOFFICE_JWT_ENABLED:
            import jwt
            token = jwt.encode(
                {'document': config['document'], 'editorConfig': config['editorConfig']},
                settings.ONLYOFFICE_JWT_SECRET,
                algorithm='HS256'
            )
            config['token'] = token

        return Response({
            'code': 0,
            'message': 'success',
            'data': {
                'config': config,
                'onlyofficeUrl': settings.ONLYOFFICE_API_URL,
                'canEdit': can_edit,
            }
        })
