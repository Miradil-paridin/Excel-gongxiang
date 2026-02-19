"""
Share 视图 - 分享功能的核心 API
"""
from django.utils import timezone
from rest_framework import generics, status, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.exceptions import PermissionDenied
from django.db.models import Q, Count, Prefetch
from .models import Share
from .serializers import ShareSerializer, ShareListSerializer
from documents.models import Document
from files.models import File


class ShareListCreateView(generics.ListCreateAPIView):
    """分享列表和创建分享"""
    serializer_class = ShareSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """获取当前用户相关的分享记录(我分享的 + 分享给我的)"""
        user = self.request.user
        # 获取活跃的分享记录
        return Share.objects.filter(
            Q(sharer=user) | Q(sharee=user),
            is_active=True
        ).select_related(
            'sharer', 'sharee', 'document', 'file'
        ).order_by('-shared_at')

    def perform_create(self, serializer):
        """创建分享时自动设置分享者"""
        serializer.save(sharer=self.request.user)


class ShareDetailView(generics.RetrieveUpdateDestroyAPIView):
    """分享详情、更新和删除"""
    serializer_class = ShareSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """只有分享者和被分享者才能访问"""
        user = self.request.user
        return Share.objects.filter(
            Q(sharer=user) | Q(sharee=user)
        ).select_related('sharer', 'sharee', 'document', 'file')

    def perform_update(self, serializer):
        """更新分享时验证权限"""
        instance = self.get_object()
        # 只有分享者才能修改分享
        if instance.sharer != self.request.user:
            raise PermissionDenied("只有分享者才能修改分享")
        # 如果过期时间已过,自动设置为非活跃状态
        if instance.expired_at and instance.expired_at < timezone.now():
            serializer.validated_data['is_active'] = False
        serializer.save()

    def perform_destroy(self, instance):
        """删除分享时验证权限"""
        # 只有分享者才能取消分享
        if instance.sharer != self.request.user:
            raise PermissionDenied("只有分享者才能取消分享")
        instance.delete()


class MySharesView(generics.ListAPIView):
    """我分享给别人的列表"""
    serializer_class = ShareListSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """获取当前用户作为分享者的记录"""
        user = self.request.user
        return Share.objects.filter(
            sharer=user,
            is_active=True
        ).select_related(
            'sharer', 'sharee', 'document', 'file'
        ).prefetch_related(
            Prefetch('document', queryset=Document.objects.filter(is_deleted=False)),
            Prefetch('file', queryset=File.objects.filter(is_deleted=False))
        ).order_by('-shared_at')

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        serializer = self.get_serializer(queryset, many=True)
        # 过滤掉目标已被删除的分享
        data = [item for item in serializer.data if item['target_id'] is not None]
        return Response(data)


class SharedWithMeView(generics.ListAPIView):
    """别人分享给我的列表"""
    serializer_class = ShareListSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """获取当前用户作为被分享者的记录"""
        user = self.request.user
        return Share.objects.filter(
            sharee=user,
            is_active=True
        ).select_related(
            'sharer', 'sharee', 'document', 'file'
        ).prefetch_related(
            Prefetch('document', queryset=Document.objects.filter(is_deleted=False)),
            Prefetch('file', queryset=File.objects.filter(is_deleted=False))
        ).order_by('-shared_at')

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        serializer = self.get_serializer(queryset, many=True)
        # 过滤掉目标已被删除的分享
        data = [item for item in serializer.data if item['target_id'] is not None]
        return Response(data)


class ShareToggleActiveView(APIView):
    """切换分享的激活状态"""
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, pk):
        try:
            share = Share.objects.get(pk=pk)
            # 只有分享者才能切换状态
            if share.sharer != request.user:
                return Response(
                    {'message': '只有分享者才能修改分享状态'},
                    status=status.HTTP_403_FORBIDDEN
                )

            share.is_active = not share.is_active
            share.save()

            return Response({
                'message': '分享状态已更新',
                'is_active': share.is_active
            })
        except Share.DoesNotExist:
            return Response(
                {'message': '分享记录不存在'},
                status=status.HTTP_404_NOT_FOUND
            )


class ShareStatsView(APIView):
    """获取分享统计信息"""
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        user = request.user

        # 我分享的次数
        my_shares_count = Share.objects.filter(
            sharer=user,
            is_active=True
        ).count()

        # 分享给我的次数
        shared_with_me_count = Share.objects.filter(
            sharee=user,
            is_active=True
        ).count()

        # 我分享的文档数量
        my_shared_documents = Document.objects.filter(
            shares__sharer=user,
            shares__is_active=True,
            is_deleted=False
        ).distinct().count()

        # 分享给我的文档数量
        shared_documents = Document.objects.filter(
            shares__sharee=user,
            shares__is_active=True,
            is_deleted=False
        ).distinct().count()

        # 我分享的文件数量
        my_shared_files = File.objects.filter(
            shares__sharer=user,
            shares__is_active=True,
            is_deleted=False
        ).distinct().count()

        # 分享给我的文件数量
        shared_files = File.objects.filter(
            shares__sharee=user,
            shares__is_active=True,
            is_deleted=False
        ).distinct().count()

        return Response({
            'my_shares_count': my_shares_count,
            'shared_with_me_count': shared_with_me_count,
            'my_shared_documents': my_shared_documents,
            'shared_documents': shared_documents,
            'my_shared_files': my_shared_files,
            'shared_files': shared_files,
        })
