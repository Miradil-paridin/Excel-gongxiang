"""
管理后台视图
"""
from rest_framework import generics, status, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from django.contrib.auth.models import Group, User
from django.db.models import Q, Count, Sum, F
from django.utils import timezone
from datetime import timedelta
from .admin_serializers import (
    AdminDepartmentSerializer,
    AdminGroupSerializer,
    AdminOrganizationSerializer,
    AdminUserCreateSerializer,
    AdminUserSerializer,
    AdminUserUpdateSerializer,
    AdminDocumentSerializer,
    AdminFileSerializer,
    AdminStatisticsSerializer
)
from .permissions import IsAdminUser
from .models import Department, Organization
from documents.models import Document
from files.models import File
from shares.models import Share


# ==================== 统计相关视图 ====================

class AdminStatisticsView(APIView):
    """统计信息视图 - 用户总数、文档总数、文件总数、分享总数"""
    permission_classes = [IsAdminUser]

    def get(self, request):
        # 用户统计
        user_total = User.objects.count()
        user_active = User.objects.filter(is_active=True).count()

        # 文档统计
        document_total = Document.objects.filter(is_deleted=False).count()

        # 文件统计
        file_total = File.objects.filter(is_deleted=False).count()

        # 分享统计
        share_total = Share.objects.filter(is_active=True).count()

        # 存储使用量 (字节)
        storage_used = File.objects.filter(is_deleted=False).aggregate(
            total=Sum('size')
        )['total'] or 0

        data = {
            'user_total': user_total,
            'user_active': user_active,
            'document_total': document_total,
            'file_total': file_total,
            'share_total': share_total,
            'storage_used': storage_used,
        }

        serializer = AdminStatisticsSerializer(data)
        return Response({
            'code': 0,
            'data': serializer.data
        })


class AdminDashboardView(APIView):
    """仪表盘数据视图 - 包含图表数据"""
    permission_classes = [IsAdminUser]

    def get(self, request):
        # 基础统计
        stats = AdminStatisticsView().get(request).data['data']

        # 最近7天的用户增长趋势
        today = timezone.now()
        user_trend = []
        doc_trend = []
        file_trend = []

        for i in range(7):
            date = today - timedelta(days=6-i)
            date_start = date.replace(hour=0, minute=0, second=0, microsecond=0)
            date_end = date.replace(hour=23, minute=59, second=59, microsecond=999999)

            # 用户增长
            new_users = User.objects.filter(
                date_joined__gte=date_start,
                date_joined__lte=date_end
            ).count()
            user_trend.append({
                'date': date.strftime('%m-%d'),
                'count': new_users
            })

            # 文档增长
            new_docs = Document.objects.filter(
                created_at__gte=date_start,
                created_at__lte=date_end,
                is_deleted=False
            ).count()
            doc_trend.append({
                'date': date.strftime('%m-%d'),
                'count': new_docs
            })

            # 文件增长
            new_files = File.objects.filter(
                created_at__gte=date_start,
                created_at__lte=date_end,
                is_deleted=False
            ).count()
            file_trend.append({
                'date': date.strftime('%m-%d'),
                'count': new_files
            })

        # 活跃用户 (最近7天登录)
        active_users = User.objects.filter(
            last_login__gte=today - timedelta(days=7)
        ).count()

        # 热门文档 (按版本更新次数)
        hot_documents = Document.objects.filter(
            is_deleted=False
        ).annotate(
            update_count=Count('id')
        ).order_by('-updated_at')[:10].values(
            'id', 'title', 'creator__username', 'updated_at', 'version'
        )

        # 热门文件 (按大小)
        hot_files = File.objects.filter(
            is_deleted=False
        ).order_by('-size')[:10].values(
            'id', 'original_name', 'uploader__username', 'size', 'created_at'
        )

        return Response({
            'code': 0,
            'data': {
                'statistics': stats,
                'user_trend': user_trend,
                'doc_trend': doc_trend,
                'file_trend': file_trend,
                'active_users': active_users,
                'hot_documents': list(hot_documents),
                'hot_files': list(hot_files),
            }
        })


# ==================== 用户管理视图 ====================

class AdminUserListView(generics.ListAPIView):
    """获取/创建用户"""
    permission_classes = [IsAdminUser]

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return AdminUserCreateSerializer
        return AdminUserSerializer

    def get_queryset(self):
        queryset = User.objects.all().order_by('-date_joined')
        keyword = self.request.query_params.get('search')
        if keyword:
            queryset = queryset.filter(
                Q(username__icontains=keyword)
                | Q(email__icontains=keyword)
                | Q(first_name__icontains=keyword)
                | Q(last_name__icontains=keyword)
            )

        org_id = self.request.query_params.get('organization')
        if org_id:
            queryset = queryset.filter(profile__organization_id=org_id)

        dept_id = self.request.query_params.get('department')
        if dept_id:
            queryset = queryset.filter(profile__department_id=dept_id)

        group_id = self.request.query_params.get('group')
        if group_id:
            queryset = queryset.filter(groups__id=group_id)

        return queryset.distinct()

    def list(self, request, *args, **kwargs):
        serializer = self.get_serializer(self.get_queryset(), many=True)
        return Response({'code': 0, 'data': serializer.data})

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        return Response(
            {
                'code': 0,
                'message': '用户创建成功',
                'data': AdminUserSerializer(user).data,
            },
            status=status.HTTP_201_CREATED,
        )


class AdminUserDetailView(generics.RetrieveUpdateDestroyAPIView):
    """用户详情、更新、删除"""
    permission_classes = [IsAdminUser]
    queryset = User.objects.all()

    def get_serializer_class(self):
        if self.request.method in ('PUT', 'PATCH'):
            return AdminUserUpdateSerializer
        return AdminUserSerializer

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        return Response({'code': 0, 'data': AdminUserSerializer(instance).data})

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        # 返回完整用户信息
        user_serializer = AdminUserSerializer(user)
        return Response({
            'code': 0,
            'message': '用户信息更新成功',
            'data': user_serializer.data
        })

    def destroy(self, request, *args, **kwargs):
        user = self.get_object()
        if not request.user.is_superuser:
            return Response(
                {'code': 1, 'message': '仅超级管理员可删除用户'},
                status=status.HTTP_403_FORBIDDEN,
            )

        if user.is_superuser:
            return Response(
                {'code': 1, 'message': '不能删除超级管理员账号'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if user == request.user:
            return Response(
                {'code': 1, 'message': '不能删除当前登录账号'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        user.delete()
        return Response({'code': 0, 'message': '用户已删除'})


# ==================== 组织架构管理视图 ====================

class AdminOrganizationListCreateView(generics.ListCreateAPIView):
    permission_classes = [IsAdminUser]
    serializer_class = AdminOrganizationSerializer
    queryset = Organization.objects.all().order_by('name')

    def list(self, request, *args, **kwargs):
        serializer = self.get_serializer(self.get_queryset(), many=True)
        return Response({'code': 0, 'data': serializer.data})

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        org = serializer.save()
        return Response(
            {'code': 0, 'message': '单位创建成功', 'data': self.get_serializer(org).data},
            status=status.HTTP_201_CREATED,
        )


class AdminOrganizationDetailView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAdminUser]
    serializer_class = AdminOrganizationSerializer
    queryset = Organization.objects.all()

    def retrieve(self, request, *args, **kwargs):
        return Response({'code': 0, 'data': self.get_serializer(self.get_object()).data})

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        serializer = self.get_serializer(self.get_object(), data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        instance = serializer.save()
        return Response({'code': 0, 'message': '单位更新成功', 'data': self.get_serializer(instance).data})

    def destroy(self, request, *args, **kwargs):
        if not request.user.is_superuser:
            return Response(
                {'code': 1, 'message': '仅超级管理员可删除单位'},
                status=status.HTTP_403_FORBIDDEN,
            )
        self.get_object().delete()
        return Response({'code': 0, 'message': '单位已删除'})


class AdminDepartmentListCreateView(generics.ListCreateAPIView):
    permission_classes = [IsAdminUser]
    serializer_class = AdminDepartmentSerializer

    def get_queryset(self):
        queryset = Department.objects.select_related('organization', 'parent').order_by('organization__name', 'name')
        org_id = self.request.query_params.get('organization')
        if org_id:
            queryset = queryset.filter(organization_id=org_id)
        return queryset

    def list(self, request, *args, **kwargs):
        serializer = self.get_serializer(self.get_queryset(), many=True)
        return Response({'code': 0, 'data': serializer.data})

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        dept = serializer.save()
        return Response(
            {'code': 0, 'message': '部门创建成功', 'data': self.get_serializer(dept).data},
            status=status.HTTP_201_CREATED,
        )


class AdminDepartmentDetailView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAdminUser]
    serializer_class = AdminDepartmentSerializer
    queryset = Department.objects.select_related('organization', 'parent').all()

    def retrieve(self, request, *args, **kwargs):
        return Response({'code': 0, 'data': self.get_serializer(self.get_object()).data})

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        serializer = self.get_serializer(self.get_object(), data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        instance = serializer.save()
        return Response({'code': 0, 'message': '部门更新成功', 'data': self.get_serializer(instance).data})

    def destroy(self, request, *args, **kwargs):
        if not request.user.is_superuser:
            return Response(
                {'code': 1, 'message': '仅超级管理员可删除部门'},
                status=status.HTTP_403_FORBIDDEN,
            )
        self.get_object().delete()
        return Response({'code': 0, 'message': '部门已删除'})


class AdminGroupListCreateView(generics.ListCreateAPIView):
    permission_classes = [IsAdminUser]
    serializer_class = AdminGroupSerializer
    queryset = Group.objects.all().order_by('name')

    def list(self, request, *args, **kwargs):
        serializer = self.get_serializer(self.get_queryset(), many=True)
        return Response({'code': 0, 'data': serializer.data})

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        group = serializer.save()
        return Response(
            {'code': 0, 'message': '用户组创建成功', 'data': self.get_serializer(group).data},
            status=status.HTTP_201_CREATED,
        )


class AdminGroupDetailView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAdminUser]
    serializer_class = AdminGroupSerializer
    queryset = Group.objects.all()

    def retrieve(self, request, *args, **kwargs):
        return Response({'code': 0, 'data': self.get_serializer(self.get_object()).data})

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        serializer = self.get_serializer(self.get_object(), data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        group = serializer.save()
        return Response({'code': 0, 'message': '用户组更新成功', 'data': self.get_serializer(group).data})

    def destroy(self, request, *args, **kwargs):
        if not request.user.is_superuser:
            return Response(
                {'code': 1, 'message': '仅超级管理员可删除用户组'},
                status=status.HTTP_403_FORBIDDEN,
            )
        self.get_object().delete()
        return Response({'code': 0, 'message': '用户组已删除'})


# ==================== 文档管理视图 ====================

class AdminDocumentListView(generics.ListAPIView):
    """获取所有文档列表（含他人的）"""
    serializer_class = AdminDocumentSerializer
    permission_classes = [IsAdminUser]

    def get_queryset(self):
        queryset = Document.objects.all().order_by('-updated_at')

        # 按创建者筛选
        creator_id = self.request.query_params.get('creator', None)
        if creator_id:
            queryset = queryset.filter(creator_id=creator_id)

        # 按类型筛选
        doc_type = self.request.query_params.get('type', None)
        if doc_type:
            queryset = queryset.filter(type=doc_type)

        # 按删除状态筛选
        is_deleted = self.request.query_params.get('is_deleted', None)
        if is_deleted is not None:
            queryset = queryset.filter(is_deleted=(is_deleted == 'true'))

        return queryset


class AdminDocumentDeleteView(APIView):
    """管理员删除任意文档"""
    permission_classes = [IsAdminUser]

    def delete(self, request, pk):
        try:
            document = Document.objects.get(pk=pk)
            document.is_deleted = True
            document.save()

            return Response({
                'code': 0,
                'message': '文档已删除'
            })
        except Document.DoesNotExist:
            return Response({
                'code': 1,
                'message': '文档不存在'
            }, status=status.HTTP_404_NOT_FOUND)


class AdminDocumentForceDeleteView(APIView):
    """管理员彻底删除文档（从数据库移除）"""
    permission_classes = [IsAdminUser]

    def delete(self, request, pk):
        try:
            document = Document.objects.get(pk=pk)
            doc_title = document.title
            document.delete()

            return Response({
                'code': 0,
                'message': f'文档 "{doc_title}" 已彻底删除'
            })
        except Document.DoesNotExist:
            return Response({
                'code': 1,
                'message': '文档不存在'
            }, status=status.HTTP_404_NOT_FOUND)


# ==================== 文件管理视图 ====================

class AdminFileListView(generics.ListAPIView):
    """获取所有文件列表（含他人的）"""
    serializer_class = AdminFileSerializer
    permission_classes = [IsAdminUser]

    def get_queryset(self):
        queryset = File.objects.all().order_by('-created_at')

        # 按上传者筛选
        uploader_id = self.request.query_params.get('uploader', None)
        if uploader_id:
            queryset = queryset.filter(uploader_id=uploader_id)

        # 按删除状态筛选
        is_deleted = self.request.query_params.get('is_deleted', None)
        if is_deleted is not None:
            queryset = queryset.filter(is_deleted=(is_deleted == 'true'))

        # 按文件类型筛选
        mime_type = self.request.query_params.get('mime_type', None)
        if mime_type:
            queryset = queryset.filter(mime_type__icontains=mime_type)

        return queryset


class AdminFileDeleteView(APIView):
    """管理员删除任意文件"""
    permission_classes = [IsAdminUser]

    def delete(self, request, pk):
        try:
            file_obj = File.objects.get(pk=pk)
            file_name = file_obj.original_name
            file_obj.is_deleted = True
            file_obj.save()

            return Response({
                'code': 0,
                'message': f'文件 "{file_name}" 已删除'
            })
        except File.DoesNotExist:
            return Response({
                'code': 1,
                'message': '文件不存在'
            }, status=status.HTTP_404_NOT_FOUND)


class AdminFileForceDeleteView(APIView):
    """管理员彻底删除文件（从数据库和磁盘移除）"""
    permission_classes = [IsAdminUser]

    def delete(self, request, pk):
        try:
            file_obj = File.objects.get(pk=pk)
            file_name = file_obj.original_name

            # 删除磁盘文件
            if file_obj.file and file_obj.file.path:
                import os
                if os.path.exists(file_obj.file.path):
                    os.remove(file_obj.file.path)

            # 从数据库删除
            file_obj.delete()

            return Response({
                'code': 0,
                'message': f'文件 "{file_name}" 已彻底删除'
            })
        except File.DoesNotExist:
            return Response({
                'code': 1,
                'message': '文件不存在'
            }, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({
                'code': 1,
                'message': f'删除失败: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# ==================== 分享管理视图 ====================

class AdminShareListView(generics.ListAPIView):
    """获取所有分享记录"""
    permission_classes = [IsAdminUser]
    serializer_class = AdminUserSerializer  # TODO: 创建专门的 Share 管理序列化器

    def get(self, request):
        # 获取所有分享记录的统计信息
        share_stats = Share.objects.values(
            'sharer__username', 'sharee__username', 'permission'
        ).annotate(
            count=Count('id')
        ).order_by('-count')[:20]

        return Response({
            'code': 0,
            'data': {
                'total_shares': Share.objects.filter(is_active=True).count(),
                'stats': list(share_stats)
            }
        })
