import logging

from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from common.view.login_view import LoginApiView
from drf import settings
from utils.es.api import ElasticSearchManager

logger = logging.getLogger("drf")


class AuditView(LoginApiView):

    def get(self, request):
        search = request.query_params.get('search')
        start_time = request.query_params.get('start_time')
        end_time = request.query_params.get('end_time')
        limit = request.query_params.get('limit')
        offset = request.query_params.get('offset')

        should, must = [], []
        if search:
            should.extend([
                {"wildcard": {"api": f'*{search}*'}},
                {"wildcard": {"user_ip": f'*{search}*'}},
                {"wildcard": {"method": f'*{search}*'}},
                {"wildcard": {"name": f'*{search}*'}},
                {"wildcard": {"username": f'*{search}*'}},
                {"wildcard": {"params": f'*{search}*'}},
                {"wildcard": {"detail": f'*{search}*'}},
                {"wildcard": {"url_name": f'*{search}*'}},
                {"wildcard": {"user_agent": f'*{search}*'}},
            ]
            )
        if start_time and end_time:
            must.append({"range": {"create_date": {"gte": start_time, "lte": end_time}}})
        query = {
            "bool": {
                "should": should,
                "must": must
            }
        }
        logger.info(query)
        es = ElasticSearchManager()
        result = es.common_search(f"{settings.BASIC_AUDIT_INDEX}-*", query, limit, offset)
        return Response(result, status=status.HTTP_200_OK)
