from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from rest_framework import status
from rest_framework.test import APITestCase

from documents.models import Document
from files.models import File, FileEditableDocument


class FileOpenInEditorTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='file_editor_user',
            email='file_editor_user@example.com',
            password='Pass@123456',
        )
        self.client.force_authenticate(user=self.user)

    def test_open_excel_file_in_editor_reuses_document_for_same_user(self):
        uploaded = SimpleUploadedFile(
            'monthly.xlsx',
            b'test-xlsx-content',
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        )
        file_obj = File.objects.create(
            file=uploaded,
            original_name='monthly.xlsx',
            uploader=self.user,
            size=uploaded.size,
            mime_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        )

        response = self.client.post(f'/api/files/{file_obj.id}/open-in-editor/')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['code'], 0)
        self.assertFalse(response.data['data']['reused'])

        document_id = response.data['data']['document_id']
        document = Document.objects.get(id=document_id)
        self.assertEqual(document.type, 'cell')
        self.assertEqual(document.creator, self.user)

        response2 = self.client.post(f'/api/files/{file_obj.id}/open-in-editor/')
        self.assertEqual(response2.status_code, status.HTTP_200_OK)
        self.assertEqual(response2.data['code'], 0)
        self.assertTrue(response2.data['data']['reused'])
        self.assertEqual(response2.data['data']['document_id'], document_id)
        self.assertEqual(Document.objects.filter(id=document_id).count(), 1)
        self.assertEqual(FileEditableDocument.objects.filter(file=file_obj, user=self.user).count(), 1)

    def test_open_unsupported_file_in_editor_rejected(self):
        uploaded = SimpleUploadedFile('archive.zip', b'zip-content', content_type='application/zip')
        file_obj = File.objects.create(
            file=uploaded,
            original_name='archive.zip',
            uploader=self.user,
            size=uploaded.size,
            mime_type='application/zip',
        )

        response = self.client.post(f'/api/files/{file_obj.id}/open-in-editor/')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['code'], 1)
