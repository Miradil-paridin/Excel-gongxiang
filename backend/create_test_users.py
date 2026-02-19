"""
创建管理员账号和测试用户的管理命令
"""
import os
import django

# 设置Django环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'docshare.settings')
django.setup()

from django.contrib.auth.models import User
from django.db import IntegrityError

def create_test_users():
    """创建测试用户"""
    users = [
        # 管理员账号
        {
            'username': 'admin',
            'email': 'admin@example.com',
            'password': 'Admin@123456',
            'is_staff': True,
            'is_superuser': True
        },
        # 普通用户
        {
            'username': 'user1',
            'email': 'user1@example.com',
            'password': 'User1@123456',
            'is_staff': False,
            'is_superuser': False
        },
        {
            'username': 'user2',
            'email': 'user2@example.com',
            'password': 'User2@123456',
            'is_staff': False,
            'is_superuser': False
        },
        {
            'username': 'user3',
            'email': 'user3@example.com',
            'password': 'User3@123456',
            'is_staff': False,
            'is_superuser': False
        },
    ]

    print("=" * 50)
    print("开始创建测试用户...")
    print("=" * 50)

    created = 0
    skipped = 0

    for user_data in users:
        try:
            user = User.objects.create_user(
                username=user_data['username'],
                email=user_data['email'],
                password=user_data['password'],
                is_staff=user_data['is_staff'],
                is_superuser=user_data['is_superuser']
            )
            print(f"✅ 成功创建用户: {user_data['username']}")
            print(f"   邮箱: {user_data['email']}")
            print(f"   密码: {user_data['password']}")
            print(f"   角色: {'管理员' if user_data['is_staff'] else '普通用户'}")
            print("-" * 50)
            created += 1
        except IntegrityError:
            print(f"⚠️  用户 {user_data['username']} 已存在，跳过")
            print("-" * 50)
            skipped += 1

    print("=" * 50)
    print(f"创建完成! 成功: {created}, 跳过: {skipped}")
    print("=" * 50)
    print("\n管理员账号:")
    print("  用户名: admin")
    print("  密码: Admin@123456")
    print("\n测试用户:")
    print("  user1 / User1@123456")
    print("  user2 / User2@123456")
    print("  user3 / User3@123456")
    print("=" * 50)

if __name__ == '__main__':
    create_test_users()
