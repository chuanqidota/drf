import json

from django.urls import resolve
from django.utils.timezone import now

from drf import settings
from utils.es.api import ElasticSearchManager


class AuditMiddleware:
    body = None  # 保存 request.body

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request, *args, **kwargs):
        self.body = request.body
        query_params = "&".join([f"{k}={v}" for k, v in request.GET.items()])

        url_match = resolve(request.path)

        content_type = None
        if request.META.get('CONTENT_TYPE'):
            content_type = request.META.get('CONTENT_TYPE').lower()

        if content_type and 'multipart/form-data' in content_type and 'boundary' in content_type:
            files = []
            for key, file in request.FILES.items():
                files.append('file: %s' % file.name)
            params = json.dumps(
                {
                    'file_name': ';'.join(files)
                }
            )
        else:
            params = self.body.decode()
        params = f"url参数:{query_params}\nbody参数-{params[:30000]}"
        doc = url_match.func.__doc__
        if doc:
            doc = doc.strip().replace('：', ':').replace(' ', '').replace(':\n', ':')
        if hasattr(url_match.func, 'actions') and doc:
            action = url_match.func.actions.get(request.method.lower())
            for s in doc.split('\n'):
                if s.startswith(action):
                    doc = s.split(':')[1]

        response = self.get_response(request)

        data = {
            'api': request.path,
            'create_date': now().strftime('%Y-%m-%d %H:%M:%S'),
            'user_ip': self.get_client_ip(request),
            'method': request.method,
            'name': request.user.name if not request.user.is_anonymous else 'AnonymousUser',
            'username': request.user.username if not request.user.is_anonymous else 'AnonymousUser',
            'params': params,
            'detail': doc,
            'url_name': url_match.url_name,
            'user_agent': request.META.get('HTTP_USER_AGENT'),
        }
        self.write_es(**data)

        return response

    @staticmethod
    def get_client_ip(request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip

    @staticmethod
    def write_es(**kwargs):
        """
            写ES数据
        :param kwargs:
        :return:
        """
        es = ElasticSearchManager()
        index = f"{settings.BASIC_AUDIT_INDEX}-{now().strftime('%Y')}"
        if not es.exist_index(index):
            mapping = {
                "api": {"type": "keyword"},
                "create_date": {"type": "datetime"},
                "user_ip": {"type": "keyword"},
                "method": {"type": "keyword"},
                "name": {"type": "keyword"},
                "username": {"type": "keyword"},
                "params": {"type": "text"},
                "detail": {"type": "text"},
                "url_name": {"type": "keyword"},
                "user_agent": {"type": "keyword"}
            }
            es.create_index_with_mapping(index, mapping)
        es.insert_timestamp_document(index, kwargs)
