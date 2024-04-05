from django.core.exceptions import PermissionDenied
from django.http import Http404
from rest_framework import exceptions
from rest_framework.response import Response
from rest_framework.views import set_rollback


def exception_handler(exc, context):
    if isinstance(exc, Http404):
        exc = exceptions.NotFound()
    elif isinstance(exc, PermissionDenied):
        exc = exceptions.PermissionDenied()

    if isinstance(exc, exceptions.APIException):
        headers = {}
        if getattr(exc, 'auth_header', None):
            headers['WWW-Authenticate'] = exc.auth_header
        if getattr(exc, 'wait', None):
            headers['Retry-After'] = '%d' % exc.wait

        if isinstance(exc.detail, str):
            data = {'message': exc.detail, 'code': 1, 'status': 'fail'}
        elif isinstance(exc.detail, list):
            data = {'message': '\n'.join(exc.detail), 'code': 1, 'status': 'fail'}
        else:
            message = []
            for k, v in exc.detail.items():
                if not isinstance(v, list):
                    message.append(str(v))
                for i in v:
                    message.append(str(i))
            data = {'message': '\n'.join(message), 'code': 1, 'status': 'fail'}
        set_rollback()
        return Response(data, status=exc.status_code, headers=headers)

    return None
