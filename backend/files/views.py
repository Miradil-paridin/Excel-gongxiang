"""
文件管理视图
"""

import os
from django.db.models import Q
from django.http import FileResponse
from django.utils import timezone
from django.core.files.base import ContentFile
from rest_framework import filters, generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from documents.models import Document
from .models import File, FileEditableDocument
from .serializers import FileSerializer


class FileListCreateView(generics.ListCreateAPIView):
    """文件列表和上传"""

    serializer_class = FileSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['original_name']
    ordering_fields = ['created_at', 'size', 'original_name']
    ordering = ['-created_at']

    def get_queryset(self):
        user = self.request.user
        queryset = File.objects.filter(
            Q(uploader=user) | Q(shares__sharee=user, shares__is_active=True)
        ).select_related('uploader').distinct()

        is_deleted = self.request.query_params.get('is_deleted')
        if is_deleted is None:
            queryset = queryset.filter(is_deleted=False)
        else:
            queryset = queryset.filter(is_deleted=(is_deleted == 'true'))

        return queryset

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            response = self.get_paginated_response(serializer.data)
            return Response(
                {
                    'code': 0,
                    'message': 'success',
                    'data': response.data['results'],
                    'count': response.data['count'],
                    'next': response.data['next'],
                    'previous': response.data['previous'],
                }
            )

        serializer = self.get_serializer(queryset, many=True)
        return Response({'code': 0, 'message': 'success', 'data': serializer.data})

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return Response(
            {'code': 0, 'message': '文件上传成功', 'data': serializer.data},
            status=status.HTTP_201_CREATED,
        )


class FileDetailView(generics.RetrieveDestroyAPIView):
    """文件详情和删除"""

    serializer_class = FileSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        return File.objects.filter(
            Q(uploader=user) | Q(shares__sharee=user, shares__is_active=True)
        ).select_related('uploader').distinct()

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response({'code': 0, 'message': 'success', 'data': serializer.data})

    def destroy(self, request, *args, **kwargs):
        file_obj = self.get_object()
        if file_obj.uploader != request.user and not request.user.is_staff:
            return Response({'code': 1, 'message': '无权删除该文件'}, status=status.HTTP_403_FORBIDDEN)

        file_obj.is_deleted = True
        file_obj.deleted_at = timezone.now()
        file_obj.save(update_fields=['is_deleted', 'deleted_at'])

        return Response({'code': 0, 'message': '文件已删除'})


class FileRestoreView(APIView):
    """恢复已删除文件"""

    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, pk):
        try:
            file_obj = File.objects.get(pk=pk, uploader=request.user, is_deleted=True)
        except File.DoesNotExist:
            return Response({'code': 1, 'message': '文件不存在或不可恢复'}, status=status.HTTP_404_NOT_FOUND)

        file_obj.is_deleted = False
        file_obj.deleted_at = None
        file_obj.save(update_fields=['is_deleted', 'deleted_at'])
        return Response({'code': 0, 'message': '文件已恢复'})


class FileDownloadView(APIView):
    """下载文件"""

    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, pk):
        try:
            file_obj = File.objects.filter(
                Q(uploader=request.user) | Q(shares__sharee=request.user, shares__is_active=True),
                is_deleted=False,
            ).select_related('uploader').distinct().get(pk=pk)
        except File.DoesNotExist:
            return Response({'code': 1, 'message': '文件不存在'}, status=status.HTTP_404_NOT_FOUND)

        if not file_obj.file:
            return Response({'code': 1, 'message': '文件内容不存在'}, status=status.HTTP_404_NOT_FOUND)

        return FileResponse(file_obj.file.open('rb'), as_attachment=True, filename=file_obj.original_name)


class FileOpenInEditorView(APIView):
    """将已上传文件转换为可在线编辑文档并返回文档ID"""

    permission_classes = [permissions.IsAuthenticated]

    EXTENSION_TO_DOC_TYPE = {
        # Word
        'docx': 'word',
        'doc': 'word',
        'odt': 'word',
        'rtf': 'word',
        'txt': 'word',
        'html': 'word',
        'htm': 'word',
        # Excel
        'xlsx': 'cell',
        'xls': 'cell',
        'ods': 'cell',
        'csv': 'cell',
        # PPT
        'pptx': 'slide',
        'ppt': 'slide',
        'odp': 'slide',
    }

    def post(self, request, pk):
        try:
            file_obj = File.objects.filter(is_deleted=False).get(pk=pk)
        except File.DoesNotExist:
            return Response({'code': 1, 'message': '文件不存在'}, status=status.HTTP_404_NOT_FOUND)

        # 仅文件所有者可一键转换编辑；管理员可代操作
        if file_obj.uploader != request.user and not request.user.is_staff:
            return Response({'code': 1, 'message': '无权将该文件转为在线文档'}, status=status.HTTP_403_FORBIDDEN)

        if not file_obj.file:
            return Response({'code': 1, 'message': '文件内容不存在'}, status=status.HTTP_404_NOT_FOUND)

        ext = os.path.splitext(file_obj.original_name or file_obj.file.name)[1].lower().replace('.', '')
        doc_type = self.EXTENSION_TO_DOC_TYPE.get(ext)
        if not doc_type:
            return Response(
                {'code': 1, 'message': '该文件类型暂不支持在线编辑'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # 同一用户重复打开同一文件时复用已有在线文档，避免重复创建
        link = FileEditableDocument.objects.filter(file=file_obj, user=request.user).select_related('document').first()
        if link and link.document and not link.document.is_deleted and link.document.file:
            return Response(
                {
                    'code': 0,
                    'message': '已复用在线文档',
                    'data': {
                        'document_id': link.document.id,
                        'title': link.document.title,
                        'type': link.document.type,
                        'reused': True,
                    },
                }
            )

        title = os.path.splitext(file_obj.original_name)[0] if file_obj.original_name else '未命名文档'
        document = Document.objects.create(
            title=title,
            type=doc_type,
            creator=request.user,
        )

        file_obj.file.open('rb')
        try:
            content = file_obj.file.read()
        finally:
            file_obj.file.close()

        document.file.save(file_obj.original_name, ContentFile(content), save=True)
        FileEditableDocument.objects.update_or_create(
            file=file_obj,
            user=request.user,
            defaults={'document': document},
        )

        return Response(
            {
                'code': 0,
                'message': '已创建在线文档',
                'data': {
                    'document_id': document.id,
                    'title': document.title,
                    'type': document.type,
                    'reused': False,
                },
            }
        )
