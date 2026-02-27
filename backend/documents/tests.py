from django.contrib.auth.models import User
from rest_framework import status
from rest_framework.test import APITestCase

from documents.models import Document


class DocumentListSmokeTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='doc_user',
            email='doc_user@example.com',
            password='Pass@123456',
        )
        Document.objects.create(title='Smoke Document', type='word', creator=self.user)

    def test_list_documents_returns_owned_document(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.get('/api/documents/')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['code'], 0)
        self.assertGreaterEqual(response.data['count'], 1)
        self.assertTrue(any(item['title'] == 'Smoke Document' for item in response.data['data']))


class DocumentVersionBehaviorTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='version_user',
            email='version_user@example.com',
            password='Pass@123456',
        )
        self.document = Document.objects.create(
            title='Version Test Doc',
            type='word',
            creator=self.user,
        )

    def test_metadata_update_does_not_bump_version_or_file_key(self):
        original_version = self.document.version
        original_file_key = self.document.file_key

        self.document.title = 'Version Test Doc Updated'
        self.document.save(update_fields=['title'])
        self.document.refresh_from_db()

        self.assertEqual(self.document.version, original_version)
        self.assertEqual(self.document.file_key, original_file_key)
