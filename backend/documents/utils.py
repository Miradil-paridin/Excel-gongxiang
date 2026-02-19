"""
OnlyOffice 工具函数
"""

import jwt
from datetime import datetime, timedelta
from django.conf import settings


def generate_file_key(document_id, version=None):
    """生成文档唯一标识 key"""
    timestamp = int(datetime.now().timestamp())
    if version:
        return f"{document_id}_{version}_{timestamp}"
    return f"{document_id}_{timestamp}"


def generate_jwt_token(payload):
    """
    生成 OnlyOffice JWT Token

    Args:
        payload: JWT 载荷数据

    Returns:
        str: JWT Token
    """
    if not settings.ONLYOFFICE_JWT_ENABLED:
        return None

    # 添加过期时间
    payload['exp'] = datetime.utcnow() + timedelta(hours=1)

    # 生成 JWT
    token = jwt.encode(
        payload,
        settings.ONLYOFFICE_JWT_SECRET,
        algorithm='HS256'
    )

    return token


def verify_jwt_token(token):
    """
    验证 OnlyOffice JWT Token

    Args:
        token: JWT Token

    Returns:
        dict: payload or None
    """
    if not settings.ONLYOFFICE_JWT_ENABLED:
        return True

    if not token:
        return False

    try:
        payload = jwt.decode(
            token,
            settings.ONLYOFFICE_JWT_SECRET,
            algorithms=['HS256']
        )
        return payload
    except jwt.ExpiredSignatureError:
        return False
    except jwt.InvalidTokenError:
        return False


def get_document_type(extension):
    """
    根据文件扩展名获取文档类型

    Args:
        extension: 文件扩展名 (不带点)

    Returns:
        str: 'word', 'cell', 'slide' or 'word'
    """
    extension = extension.lower()
    mapping = settings.ONLYOFFICE_DOCUMENT_TYPES

    return mapping.get(extension, 'word')


def get_editor_config(document, request):
    """
    生成 OnlyOffice 编辑器配置

    Args:
        document: Document 对象
        request: Django Request 对象

    Returns:
        dict: OnlyOffice 编辑器配置
    """
    from django.conf import settings

    # 获取文档的访问 URL
    if document.file:
        file_url = request.build_absolute_uri(document.file.url)
    else:
        file_url = ''

    # 获取文件扩展名
    file_ext = document.file_extension if document.file_extension else 'docx'

    # 确定文档类型
    doc_type = 'text'  # word
    if file_ext in ['xlsx', 'xls', 'ods', 'csv']:
        doc_type = 'spreadsheet'
    elif file_ext in ['pptx', 'ppt', 'odp']:
        doc_type = 'presentation'

    # 回调 URL
    callback_url = request.build_absolute_uri('/api/documents/callback/')

    # 编辑器配置
    config = {
        "document": {
            "fileType": file_ext,
            "key": document.file_key or generate_file_key(document.id, document.version),
            "title": document.title,
            "url": file_url,
            "permissions": {
                "comment": True,
                "copy": True,
                "download": True,
                "edit": True,
                "print": True,
                "review": True
            }
        },
        "documentType": doc_type,
        "editorConfig": {
            "callbackUrl": callback_url,
            "mode": "edit",
            "lang": "zh-CN",
            "user": {
                "id": str(request.user.id),
                "name": request.user.username or '匿名用户'
            },
            "embedded": {
                "saveUrl": file_url,
                "embedUrl": file_url,
                "shareUrl": file_url,
                "toolbarDocked": "top"
            }
        }
    }

    # 如果启用 JWT，添加 token
    if settings.ONLYOFFICE_JWT_ENABLED:
        config['token'] = generate_jwt_token({
            'document_key': document.file_key,
            'user_id': request.user.id
        })
        config['editorConfig']['token'] = generate_jwt_token({
            'user_id': request.user.id
        })

    return config


def get_file_type_for_onlyoffice(extension):
    """
    根据扩展名返回 OnlyOffice 支持的文件类型

    Args:
        extension: 文件扩展名

    Returns:
        str: OnlyOffice 文件类型后缀
    """
    ext = extension.lower()
    doc_exts = ['doc', 'odt', 'rtf', 'txt', 'html', 'htm']
    cell_exts = ['xls', 'ods', 'csv']
    slide_exts = ['ppt', 'odp']

    if ext in doc_exts:
        return 'docx'
    elif ext in cell_exts:
        return 'xlsx'
    elif ext in slide_exts:
        return 'pptx'
    else:
        return ext
