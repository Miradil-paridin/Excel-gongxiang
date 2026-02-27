from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from rest_framework import status
from rest_framework.test import APITestCase

from accounts.models import Department, Organization, UserProfile
from .models import Submission, TaskAssignment, Template


class WorkflowSmokeTests(APITestCase):
    def setUp(self):
        self.admin = User.objects.create_user(
            username='wf_admin',
            email='wf_admin@example.com',
            password='Admin@123456',
            is_staff=True,
        )
        self.user1 = User.objects.create_user(
            username='wf_user1',
            email='wf_user1@example.com',
            password='User1@123456',
        )

        self.org = Organization.objects.create(name='总部', code='HQ')
        self.dept = Department.objects.create(name='财务部', code='FIN', organization=self.org)
        UserProfile.objects.create(user=self.user1, organization=self.org, department=self.dept)

        self.template = Template.objects.create(
            name='月报模板',
            category='finance',
            created_by=self.admin,
            file=SimpleUploadedFile(
                'template.xlsx',
                b'fake excel bytes',
                content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            ),
            editable_cells=[{'sheet': 'Sheet1', 'cells': ['B2', 'B3']}],
        )

    def test_admin_can_create_task_and_generate_assignment(self):
        self.client.force_authenticate(self.admin)
        payload = {
            'title': '2026年2月财务填报',
            'description': '请按模板填写',
            'template': self.template.id,
            'target_users': [self.user1.id],
            'status': 'active',
        }
        response = self.client.post('/api/tasks/', payload, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        assignment_exists = TaskAssignment.objects.filter(task_id=response.data['id'], assignee=self.user1).exists()
        self.assertTrue(assignment_exists)

        task_id = response.data['id']
        from .models import DistributionTask
        task = DistributionTask.objects.get(id=task_id)
        self.assertEqual(task.template_version, self.template.version)
        self.assertTrue(bool(task.template_snapshot_file))

    def test_assignee_can_submit_workflow(self):
        self.client.force_authenticate(self.admin)
        task_resp = self.client.post(
            '/api/tasks/',
            {
                'title': '提交流程测试',
                'template': self.template.id,
                'target_users': [self.user1.id],
                'status': 'active',
            },
            format='json',
        )
        self.assertEqual(task_resp.status_code, status.HTTP_201_CREATED)

        assignment = TaskAssignment.objects.get(task_id=task_resp.data['id'], assignee=self.user1)
        self.client.force_authenticate(self.user1)
        create_resp = self.client.post(
            '/api/submissions/',
            {'assignment': assignment.id, 'extracted_data': {'B2': 123}},
            format='json',
        )
        self.assertEqual(create_resp.status_code, status.HTTP_201_CREATED)

        submit_resp = self.client.post(f"/api/submissions/{create_resp.data['id']}/submit/")
        self.assertEqual(submit_resp.status_code, status.HTTP_200_OK)

        submission = Submission.objects.get(id=create_resp.data['id'])
        assignment.refresh_from_db()
        self.assertEqual(submission.status, 'submitted')
        self.assertEqual(assignment.status, 'submitted')

        # 已提交再次创建/编辑可转草稿，撤回后继续编辑再提交
        withdraw_resp = self.client.post(f"/api/submissions/{create_resp.data['id']}/withdraw/")
        self.assertEqual(withdraw_resp.status_code, status.HTTP_200_OK)

        edit_resp = self.client.post(
            '/api/submissions/',
            {'assignment': assignment.id, 'extracted_data': {'B2': 456}},
            format='json',
        )
        self.assertEqual(edit_resp.status_code, status.HTTP_201_CREATED)

    def test_invalid_transition_rejected(self):
        self.client.force_authenticate(self.admin)
        task_resp = self.client.post(
            '/api/tasks/',
            {'title': '非法流转测试', 'template': self.template.id, 'target_users': [self.user1.id]},
            format='json',
        )
        self.assertEqual(task_resp.status_code, status.HTTP_201_CREATED)
        assignment = TaskAssignment.objects.get(task_id=task_resp.data['id'], assignee=self.user1)

        self.client.force_authenticate(self.user1)
        create_resp = self.client.post('/api/submissions/', {'assignment': assignment.id}, format='json')
        self.assertEqual(create_resp.status_code, status.HTTP_201_CREATED)

        # draft 状态直接撤回应被拒绝
        withdraw_resp = self.client.post(f"/api/submissions/{create_resp.data['id']}/withdraw/")
        self.assertEqual(withdraw_resp.status_code, status.HTTP_400_BAD_REQUEST)
