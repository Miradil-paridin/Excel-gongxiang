from django.contrib.auth.models import User
from rest_framework import status
from rest_framework.test import APITestCase

from accounts.models import Department, Organization


class LoginSmokeTests(APITestCase):
    def setUp(self):
        self.password = 'Pass@123456'
        self.user = User.objects.create_user(
            username='smoke_user',
            email='smoke@example.com',
            password=self.password,
        )

    def test_login_returns_token(self):
        response = self.client.post(
            '/api/auth/login/',
            {'username': self.user.username, 'password': self.password},
            format='json',
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['code'], 0)
        self.assertIn('token', response.data['data'])


class AdminUserManagementTests(APITestCase):
    def setUp(self):
        self.admin = User.objects.create_user(
            username='admin_smoke',
            email='admin_smoke@example.com',
            password='Admin@123456',
            is_staff=True,
        )
        self.client.force_authenticate(user=self.admin)

        self.org = Organization.objects.create(name='测试单位', code='ORG001')
        self.dept = Department.objects.create(
            name='测试部门',
            code='DEP001',
            organization=self.org,
        )

    def test_admin_can_create_user_with_org_department(self):
        response = self.client.post(
            '/api/auth/admin/users/',
            {
                'username': 'new_member',
                'email': 'new_member@example.com',
                'password': 'Pass@123456',
                'organization': self.org.id,
                'department': self.dept.id,
                'role_title': '产品经理',
                'is_staff': False,
                'is_active': True,
            },
            format='json',
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['code'], 0)
        self.assertEqual(response.data['data']['organization_name'], '测试单位')
        self.assertEqual(response.data['data']['department_name'], '测试部门')

    def test_non_super_admin_cannot_create_staff_user(self):
        response = self.client.post(
            '/api/auth/admin/users/',
            {
                'username': 'staff_member',
                'email': 'staff_member@example.com',
                'password': 'Pass@123456',
                'is_staff': True,
                'is_active': True,
            },
            format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_admin_can_list_organizations_and_departments(self):
        org_res = self.client.get('/api/auth/admin/organizations/')
        dept_res = self.client.get('/api/auth/admin/departments/')

        self.assertEqual(org_res.status_code, status.HTTP_200_OK)
        self.assertEqual(org_res.data['code'], 0)
        self.assertEqual(dept_res.status_code, status.HTTP_200_OK)
        self.assertEqual(dept_res.data['code'], 0)

    def test_non_super_admin_cannot_delete_user(self):
        victim = User.objects.create_user(
            username='victim_user',
            email='victim@example.com',
            password='Pass@123456',
        )
        response = self.client.delete(f'/api/auth/admin/users/{victim.id}/')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
