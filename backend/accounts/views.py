"""
用户认证视图
"""

from rest_framework import status, generics
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth.models import User
from django.contrib.auth import logout
from .serializers import (
    UserSerializer,
    UserRegisterSerializer,
    UserLoginSerializer,
    ChangePasswordSerializer
)
from .permissions import IsAdminUser


def get_tokens_for_user(user):
    """获取JWT Token"""
    refresh = RefreshToken.for_user(user)
    return {
        'refresh': str(refresh),
        'access': str(refresh.access_token),
    }


class RegisterView(generics.CreateAPIView):
    """用户注册视图"""
    queryset = User.objects.all()
    serializer_class = UserRegisterSerializer
    permission_classes = [AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        # 生成Token
        tokens = get_tokens_for_user(user)

        return Response({
            'code': 0,
            'message': '注册成功',
            'data': {
                'user': UserSerializer(user).data,
                'token': tokens['access']
            }
        }, status=status.HTTP_201_CREATED)


class LoginView(generics.GenericAPIView):
    """用户登录视图"""
    serializer_class = UserLoginSerializer
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']

        # 生成Token
        tokens = get_tokens_for_user(user)

        return Response({
            'code': 0,
            'message': '登录成功',
            'data': {
                'token': tokens['access'],
                'user': UserSerializer(user).data
            }
        })


class UserInfoView(generics.RetrieveAPIView):
    """获取当前用户信息"""
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user

    def retrieve(self, request, *args, **kwargs):
        user = self.get_object()
        serializer = self.get_serializer(user)
        return Response({
            'code': 0,
            'data': serializer.data
        })


class ChangePasswordView(generics.GenericAPIView):
    """修改密码视图"""
    serializer_class = ChangePasswordSerializer
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)

        # 设置新密码
        request.user.set_password(serializer.validated_data['new_password'])
        request.user.save()

        # 注销当前会话，需要重新登录
        logout(request)

        return Response({
            'code': 0,
            'message': '密码修改成功，请重新登录'
        })


class UserListView(generics.ListAPIView):
    """用户列表视图（用于选择分享对象）"""
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """排除当前用户"""
        return User.objects.exclude(id=self.request.user.id).order_by('username')

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response({
            'code': 0,
            'data': serializer.data
        })
