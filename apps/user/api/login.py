from django.contrib.auth import logout, authenticate, login
from django.http import HttpResponseRedirect
from django.shortcuts import resolve_url
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from common.view.login_view import LoginApiView
from drf import settings


class LoginView(APIView):
    permission_classes = (AllowAny,)
    tags = ["登录"]
    operation_id = "登录"

    def dispatch(self, request, *args, **kwargs):
        """
        用户登录
        """
        return Response(status=settings.UNLOGIN_STATUS)


class LogoutView(LoginApiView):
    http_method_names = ['get']
    tags = ["登录"]
    operation_id = "登出"

    def get(self, request):
        """
        用户登出
        """
        logout(self.request)
        login_url = resolve_url(settings.LOGIN_URL)
        resp = HttpResponseRedirect(login_url)
        return resp


class ManualLoginView(APIView):
    permission_classes = (AllowAny,)
    tags = ["登录"]
    operation_id = "手动登录"

    def post(self, request):
        """
            手动登录
        :param request:
        :return:
        """
        username = self.request.data.get('username', '')
        password = self.request.data.get('password', '')
        user = authenticate(request, username=username, password=password)
        if not user:
            return Response(data={'message': '无效的用户名和密码'}, status=status.HTTP_400_BAD_REQUEST)
        try:
            login(request, user)
            return Response(data={"msg": "登录成功"}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response(data={"msg": f"登录失败-{repr(e)}"}, status=status.HTTP_400_BAD_REQUEST)
