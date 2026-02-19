"""
Share 路由配置
"""
from django.urls import path
from . import views

urlpatterns = [
    # 分享列表和创建
    path('shares/', views.ShareListCreateView.as_view(), name='share-list-create'),

    # 分享详情、更新、删除
    path('shares/<int:pk>/', views.ShareDetailView.as_view(), name='share-detail'),

    # 我分享给别人的列表
    path('shares/my-shares/', views.MySharesView.as_view(), name='my-shares'),

    # 别人分享给我的列表
    path('shares/shared-with-me/', views.SharedWithMeView.as_view(), name='shared-with-me'),

    # 切换分享激活状态
    path('shares/<int:pk>/toggle/', views.ShareToggleActiveView.as_view(), name='share-toggle'),

    # 分享统计信息
    path('shares/stats/', views.ShareStatsView.as_view(), name='share-stats'),
]
