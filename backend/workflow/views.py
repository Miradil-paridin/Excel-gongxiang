from django.db.models import Count
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from accounts.permissions import IsAdminUser
from .models import DistributionTask, Submission, TaskAssignment, Template
from .serializers import (
    DistributionTaskSerializer,
    SubmissionSerializer,
    TaskAssignmentSerializer,
    TemplateSerializer,
)


class TemplateListCreateView(generics.ListCreateAPIView):
    serializer_class = TemplateSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        queryset = Template.objects.all()
        if not self.request.user.is_staff:
            queryset = queryset.filter(is_active=True)
        return queryset.order_by('-updated_at')

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)


class TemplateDetailView(generics.RetrieveUpdateAPIView):
    serializer_class = TemplateSerializer
    permission_classes = [permissions.IsAuthenticated]
    queryset = Template.objects.all()

    def update(self, request, *args, **kwargs):
        if not request.user.is_staff:
            return Response({'message': '仅管理员可修改模板'}, status=status.HTTP_403_FORBIDDEN)
        return super().update(request, *args, **kwargs)


class TaskListCreateView(generics.ListCreateAPIView):
    serializer_class = DistributionTaskSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.is_staff:
            return DistributionTask.objects.all().select_related('template', 'created_by').order_by('-created_at')
        return DistributionTask.objects.filter(assignments__assignee=user).select_related('template', 'created_by').distinct().order_by(
            '-created_at'
        )

    def create(self, request, *args, **kwargs):
        if not request.user.is_staff:
            return Response({'message': '仅管理员可创建任务'}, status=status.HTTP_403_FORBIDDEN)
        return super().create(request, *args, **kwargs)

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)


class TaskDetailView(generics.RetrieveAPIView):
    serializer_class = DistributionTaskSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        if self.request.user.is_staff:
            return DistributionTask.objects.all().select_related('template', 'created_by')
        return DistributionTask.objects.filter(assignments__assignee=self.request.user).select_related(
            'template', 'created_by'
        ).distinct()


class TaskProgressView(APIView):
    permission_classes = [permissions.IsAuthenticated, IsAdminUser]

    def get(self, request, pk):
        try:
            task = DistributionTask.objects.get(pk=pk)
        except DistributionTask.DoesNotExist:
            return Response({'message': '任务不存在'}, status=status.HTTP_404_NOT_FOUND)

        stats = task.assignments.values('status').annotate(count=Count('id'))
        summary = {item['status']: item['count'] for item in stats}
        return Response(
            {
                'task_id': task.id,
                'task_title': task.title,
                'total': task.assignments.count(),
                'pending': summary.get('pending', 0),
                'draft': summary.get('draft', 0),
                'submitted': summary.get('submitted', 0),
                'returned': summary.get('returned', 0),
                'approved': summary.get('approved', 0),
                'withdrawn': summary.get('withdrawn', 0),
                'expired': summary.get('expired', 0),
            }
        )


class MyTaskAssignmentsView(generics.ListAPIView):
    serializer_class = TaskAssignmentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        queryset = TaskAssignment.objects.filter(assignee=self.request.user).select_related('task', 'task__template')
        status_filter = self.request.query_params.get('status')
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        return queryset.order_by('-created_at')


class SubmissionCreateView(generics.CreateAPIView):
    serializer_class = SubmissionSerializer
    permission_classes = [permissions.IsAuthenticated]


class SubmissionDetailView(generics.RetrieveUpdateAPIView):
    serializer_class = SubmissionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        if self.request.user.is_staff:
            return Submission.objects.all().select_related('task', 'assignment', 'user')
        return Submission.objects.filter(user=self.request.user).select_related('task', 'assignment', 'user')

    def update(self, request, *args, **kwargs):
        submission = self.get_object()
        if submission.status == 'submitted':
            return Response({'message': '已上报数据不能直接修改，请先撤回'}, status=status.HTTP_400_BAD_REQUEST)
        return super().update(request, *args, **kwargs)


class SubmissionSubmitView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, pk):
        try:
            submission = Submission.objects.select_related('assignment').get(pk=pk, user=request.user)
        except Submission.DoesNotExist:
            return Response({'message': '提交记录不存在'}, status=status.HTTP_404_NOT_FOUND)

        assignment = submission.assignment
        try:
            submission.transition_to('submitted')
            assignment.transition_to('submitted')
        except ValueError as exc:
            return Response({'message': str(exc)}, status=status.HTTP_400_BAD_REQUEST)

        submission.save()
        assignment.save()

        return Response({'message': '上报成功'})


class SubmissionWithdrawView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, pk):
        try:
            submission = Submission.objects.select_related('assignment').get(pk=pk, user=request.user)
        except Submission.DoesNotExist:
            return Response({'message': '提交记录不存在'}, status=status.HTTP_404_NOT_FOUND)

        assignment = submission.assignment
        try:
            submission.transition_to('withdrawn')
            assignment.transition_to('withdrawn')
        except ValueError as exc:
            return Response({'message': str(exc)}, status=status.HTTP_400_BAD_REQUEST)

        submission.save()
        assignment.save()
        return Response({'message': '已撤回'})


class SubmissionReturnView(APIView):
    permission_classes = [permissions.IsAuthenticated, IsAdminUser]

    def post(self, request, pk):
        reason = (request.data.get('reason') or '').strip()
        if not reason:
            return Response({'message': '退回原因不能为空'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            submission = Submission.objects.select_related('assignment').get(pk=pk)
        except Submission.DoesNotExist:
            return Response({'message': '提交记录不存在'}, status=status.HTTP_404_NOT_FOUND)

        assignment = submission.assignment
        try:
            submission.transition_to('returned', reason=reason)
            assignment.transition_to('returned', reason=reason)
        except ValueError as exc:
            return Response({'message': str(exc)}, status=status.HTTP_400_BAD_REQUEST)

        submission.save()
        assignment.save()

        return Response({'message': '已退回'})
