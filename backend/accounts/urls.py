"""
accounts 应用 URL 配置
"""

from django.urls import path
from . import views

urlpatterns = [
    # 用户注册
    path('register/', views.RegisterView.as_view(), name='register'),
    # 用户登录
    path('login/', views.LoginView.as_view(), name='login'),
    # 获取当前用户信息
    path('me/', views.UserInfoView.as_view(), name='user-info'),
    # 修改密码
    path('change-password/', views.ChangePasswordView.as_view(), name='change-password'),
    # 用户列表（用于选择分享对象）
    path('users/', views.UserListView.as_view(), name='user-list'),
]
