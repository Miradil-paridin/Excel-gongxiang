from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from rest_framework import status
from rest_framework.test import APITestCase

from documents.models import Document
from files.models import File
from shares.models import Share


class ShareListSmokeTests(APITestCase):
    def setUp(self):
        self.sharer = User.objects.create_user(
            username='sharer',
            email='sharer@example.com',
            password='Pass@123456',
        )
        self.sharee = User.objects.create_user(
            username='sharee',
            email='sharee@example.com',
            password='Pass@123456',
        )

        self.document = Document.objects.create(
            title='Shared Smoke Doc',
            type='word',
            creator=self.sharer,
        )

        Share.objects.create(
            document=self.document,
            sharer=self.sharer,
            sharee=self.sharee,
            permission='read',
            is_active=True,
        )

    def test_shared_with_me_list_contains_shared_document(self):
        self.client.force_authenticate(user=self.sharee)
        response = self.client.get('/api/shares/shared-with-me/')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(any(item['target_id'] == self.document.id for item in response.data))


class ShareCreateCopyTests(APITestCase):
    def setUp(self):
        self.sharer = User.objects.create_user(
            username='copy_sharer',
            email='copy_sharer@example.com',
            password='Pass@123456',
        )
        self.sharee = User.objects.create_user(
            username='copy_sharee',
            email='copy_sharee@example.com',
            password='Pass@123456',
        )

    def test_create_copy_from_shared_document(self):
        source_document = Document.objects.create(
            title='统计模板',
            type='cell',
            creator=self.sharer,
        )
        source_document.file.save(
            'template.xlsx',
            SimpleUploadedFile(
                'template.xlsx',
                b'fake excel bytes',
                content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            ),
            save=True,
        )
        share = Share.objects.create(
            document=source_document,
            sharer=self.sharer,
            sharee=self.sharee,
            permission='read',
            is_active=True,
        )

        self.client.force_authenticate(user=self.sharee)
        response = self.client.post(f'/api/shares/{share.id}/create-copy/')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        new_doc_id = response.data['data']['document_id']
        copied_document = Document.objects.get(id=new_doc_id)
        self.assertEqual(copied_document.creator, self.sharee)
        self.assertEqual(copied_document.type, 'cell')
        self.assertIn('填写副本', copied_document.title)
        self.assertTrue(bool(copied_document.file))

    def test_create_copy_from_unsupported_file_returns_400(self):
        source_file = File.objects.create(
            file=SimpleUploadedFile('archive.zip', b'zip bytes', content_type='application/zip'),
            original_name='archive.zip',
            uploader=self.sharer,
        )
        share = Share.objects.create(
            file=source_file,
            sharer=self.sharer,
            sharee=self.sharee,
            permission='read',
            is_active=True,
        )

        self.client.force_authenticate(user=self.sharee)
        response = self.client.post(f'/api/shares/{share.id}/create-copy/')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
