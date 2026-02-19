"""
OnlyOffice 回调视图
处理文档保存等回调请求
"""

import json
import logging
import requests
from datetime import datetime
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.conf import settings
from .utils import verify_jwt_token
from .models import Document

logger = logging.getLogger(__name__)


@csrf_exempt
@require_http_methods(["POST"])
def document_callback(request):
    """
    OnlyOffice 文档保存回调接口

    OnlyOffice 会在以下情况调用此接口:
    - status=1: 文档准备就绪
    - status=2: 文档已保存
    - status=3: 文档强制保存
    - status=4: 文档保存错误
    - status=6: 文档关闭
    """
    # 验证 JWT Token (如果启用)
    if settings.ONLYOFFICE_JWT_ENABLED:
        token = request.headers.get(settings.ONLYOFFICE_JWT_HEADER)
        if not token or not verify_jwt_token(token):
            return JsonResponse({'error': 1})

    try:
        data = json.loads(request.body)
        logger.info(f"OnlyOffice callback received: {data}")

        status = data.get('status')
        file_key = data.get('key')

        if status in [2, 3]:  # 已保存或强制保存
            # 获取下载地址
            url = data.get('url')
            if url:
                # 下载并保存文件
                success = download_and_save_document(file_key, url)
                if success:
                    return JsonResponse({'error': 0})
                else:
                    return JsonResponse({'error': 1})
            else:
                logger.error(f"No URL in callback data: {data}")
                return JsonResponse({'error': 1})

        elif status == 1:  # 准备就绪
            logger.info(f"Document {file_key} is ready")
            return JsonResponse({'error': 0})

        elif status == 6:  # 文档关闭
            logger.info(f"Document {file_key} closed")
            return JsonResponse({'error': 0})

        else:
            logger.warning(f"Unhandled status {status}: {data}")
            return JsonResponse({'error': 0})

    except Exception as e:
        logger.error(f"Error processing OnlyOffice callback: {e}", exc_info=True)
        return JsonResponse({'error': 1})


def download_and_save_document(file_key, download_url):
    """
    下载并保存文档

    Args:
        file_key: 文档唯一标识
        download_url: OnlyOffice 提供的下载地址

    Returns:
        bool: 是否成功
    """
    try:
        # 从 file_key 解析 document_id
        parts = file_key.split('_')
        if len(parts) < 2:
            logger.error(f"Invalid file_key format: {file_key}")
            return False

        document_id = parts[0]

        # 获取文档对象
        try:
            document = Document.objects.get(id=document_id)
        except Document.DoesNotExist:
            logger.error(f"Document {document_id} not found")
            return False

        # 下载文件
        response = requests.get(download_url, timeout=30)
        response.raise_for_status()

        # 保存文件
        file_name = document.file.name if document.file else f"document_{document_id}.docx"
        with open(document.file.path, 'wb') as f:
            f.write(response.content)

        # 更新文档
        document.updated_at = datetime.now()
        document.save(update_fields=['updated_at'])

        logger.info(f"Document {document_id} saved successfully")
        return True

    except Exception as e:
        logger.error(f"Error downloading document: {e}", exc_info=True)
        return False
