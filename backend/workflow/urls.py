from django.urls import path

from . import views

urlpatterns = [
    path('templates/', views.TemplateListCreateView.as_view(), name='template-list-create'),
    path('templates/<int:pk>/', views.TemplateDetailView.as_view(), name='template-detail'),
    path('tasks/', views.TaskListCreateView.as_view(), name='task-list-create'),
    path('tasks/<int:pk>/', views.TaskDetailView.as_view(), name='task-detail'),
    path('tasks/<int:pk>/progress/', views.TaskProgressView.as_view(), name='task-progress'),
    path('submissions/my-tasks/', views.MyTaskAssignmentsView.as_view(), name='my-task-assignments'),
    path('submissions/', views.SubmissionCreateView.as_view(), name='submission-create'),
    path('submissions/<int:pk>/', views.SubmissionDetailView.as_view(), name='submission-detail'),
    path('submissions/<int:pk>/submit/', views.SubmissionSubmitView.as_view(), name='submission-submit'),
    path('submissions/<int:pk>/withdraw/', views.SubmissionWithdrawView.as_view(), name='submission-withdraw'),
    path('submissions/<int:pk>/return/', views.SubmissionReturnView.as_view(), name='submission-return'),
]
