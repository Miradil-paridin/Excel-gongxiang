"""
API功能测试脚本
测试所有核心API功能
"""
import requests
import json
import time

BASE_URL = "http://localhost:8000/api"

class APITest:
    def __init__(self):
        self.session = requests.Session()
        self.token = None
        self.users = {
            'admin': {'username': 'admin', 'password': 'Admin@123456'},
            'user1': {'username': 'user1', 'password': 'User1@123456'},
            'user2': {'username': 'user2', 'password': 'User2@123456'},
        }

    def login(self, username, password):
        """登录获取Token"""
        url = f"{BASE_URL}/auth/login/"
        data = {
            'username': username,
            'password': password
        }
        response = self.session.post(url, json=data)

        if response.status_code == 200:
            result = response.json()
            self.token = result['data']['token']
            self.session.headers.update({
                'Authorization': f'Bearer {self.token}'
            })
            print(f"✅ {username} 登录成功")
            return True
        else:
            print(f"❌ {username} 登录失败: {response.text}")
            return False

    def test_auth(self):
        """测试认证功能"""
        print("\n" + "="*50)
        print("1. 测试用户认证")
        print("="*50)

        # 测试登录
        assert self.login('user1', 'User1@123456'), "登录失败"

        # 测试获取用户信息
        url = f"{BASE_URL}/auth/user/"
        response = self.session.get(url)

        if response.status_code == 200:
            print("✅ 获取用户信息成功")
            return True
        else:
            print(f"❌ 获取用户信息失败: {response.text}")
            return False

    def test_documents(self):
        """测试文档管理"""
        print("\n" + "="*50)
        print("2. 测试文档管理")
        print("="*50)

        # 创建文档
        url = f"{BASE_URL}/documents/"
        data = {
            'title': '测试文档',
            'type': 'word'
        }
        response = self.session.post(url, json=data)

        if response.status_code == 201:
            doc = response.json()['data']
            print(f"✅ 创建文档成功: {doc['title']}")
            doc_id = doc['id']

            # 获取文档列表
            response = self.session.get(url)
            if response.status_code == 200:
                print("✅ 获取文档列表成功")

            # 删除文档
            del_url = f"{BASE_URL}/documents/{doc_id}/"
            response = self.session.delete(del_url)
            if response.status_code == 200:
                print("✅ 删除文档成功")

            return True
        else:
            print(f"❌ 创建文档失败: {response.text}")
            return False

    def test_files(self):
        """测试文件管理"""
        print("\n" + "="*50)
        print("3. 测试文件管理")
        print("="*50)

        # 这里只测试列表接口，上传需要文件
        url = f"{BASE_URL}/files/"
        response = self.session.get(url)

        if response.status_code == 200:
            print("✅ 获取文件列表成功")
            return True
        else:
            print(f"❌ 获取文件列表失败: {response.text}")
            return False

    def test_shares(self):
        """测试分享功能"""
        print("\n" + "="*50)
        print("4. 测试分享功能")
        print("="*50)

        # 先创建一个测试文档
        doc_url = f"{BASE_URL}/documents/"
        doc_data = {'title': '分享测试文档', 'type': 'word'}
        response = self.session.post(doc_url, json=doc_data)

        if response.status_code != 201:
            print("❌ 创建测试文档失败")
            return False

        doc_id = response.json()['data']['id']
        print(f"✅ 创建测试文档: {doc_id}")

        # 测试分享API (需要user2的ID)
        # 先获取用户列表
        url = f"{BASE_URL}/auth/admin/users/"
        response = self.session.get(url)

        if response.status_code == 200:
            users = response.json()['data']
            user2 = next((u for u in users if u['username'] == 'user2'), None)

            if user2:
                # 创建分享
                share_url = f"{BASE_URL}/shares/"
                share_data = {
                    'document': doc_id,
                    'sharee': user2['id'],
                    'permission': 'write'
                }
                response = self.session.post(share_url, json=share_data)

                if response.status_code == 201:
                    print(f"✅ 分享文档给 {user2['username']} 成功")

                    # 测试获取我的分享
                    response = self.session.get(f"{BASE_URL}/shares/my-shares/")
                    if response.status_code == 200:
                        print("✅ 获取我的分享列表成功")

                    # 测试获取分享给我的
                    response = self.session.get(f"{BASE_URL}/shares/shared-with-me/")
                    if response.status_code == 200:
                        print("✅ 获取分享给我的列表成功")

                    # 清理测试文档
                    self.session.delete(f"{BASE_URL}/documents/{doc_id}/")
                    return True
                else:
                    print(f"❌ 分享失败: {response.text}")
                    return False
            else:
                print("❌ 找不到user2")
                return False
        else:
            print(f"❌ 获取用户列表失败: {response.text}")
            return False

    def test_admin(self):
        """测试管理后台"""
        print("\n" + "="*50)
        print("5. 测试管理后台")
        print("="*50)

        # 切换到admin账号
        if not self.login('admin', 'Admin@123456'):
            print("❌ 管理员登录失败")
            return False

        # 测试统计API
        url = f"{BASE_URL}/auth/admin/statistics/"
        response = self.session.get(url)

        if response.status_code == 200:
            stats = response.json()['data']
            print(f"✅ 获取统计信息成功")
            print(f"   用户总数: {stats['user_total']}")
            print(f"   文档总数: {stats['document_total']}")
            print(f"   文件总数: {stats['file_total']}")
            print(f"   分享总数: {stats['share_total']}")
            return True
        else:
            print(f"❌ 获取统计信息失败: {response.status_code}")
            return False

    def run_all_tests(self):
        """运行所有测试"""
        print("\n" + "="*50)
        print("开始API功能测试")
        print("="*50)

        results = []

        # 1. 认证测试
        self.login('user1', 'User1@123456')
        results.append(('用户认证', self.test_auth()))

        # 2. 文档管理测试
        results.append(('文档管理', self.test_documents()))

        # 3. 文件管理测试
        results.append(('文件管理', self.test_files()))

        # 4. 分享功能测试
        results.append(('分享功能', self.test_shares()))

        # 5. 管理后台测试
        results.append(('管理后台', self.test_admin()))

        # 输出测试结果
        print("\n" + "="*50)
        print("测试结果汇总")
        print("="*50)

        for name, passed in results:
            status = "✅ 通过" if passed else "❌ 失败"
            print(f"{name}: {status}")

        total = len(results)
        passed = sum(1 for _, p in results if p)

        print("="*50)
        print(f"总计: {passed}/{total} 通过")
        print("="*50)

        return passed == total


if __name__ == '__main__':
    print("\n" + "="*50)
    print("API功能测试脚本")
    print("="*50)
    print("\n请确保后端服务器已启动: python manage.py runserver")
    print("\n测试账号:")
    print("  admin / Admin@123456")
    print("  user1 / User1@123456")
    print("  user2 / User2@123456")

    input("\n按回车键开始测试...")

    tester = APITest()
    success = tester.run_all_tests()

    if success:
        print("\n🎉 所有测试通过!")
    else:
        print("\n⚠️  部分测试失败，请检查日志")
