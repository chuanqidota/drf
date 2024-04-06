import os

from django.contrib.auth.mixins import AccessMixin
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet

from common.view.user_view import UserModelViewSet
from drf import settings


class LoginRequiredMixin(AccessMixin):
    """
    Verify that the current user is authenticated.
    根据dev_mode: 开发时打开此选项便于使用postman调试接口
    """

    dev_mode = True if os.getenv("drfEnv") else False

    def dispatch(self, request, *args, **kwargs):
        # 生产环境强制开启登录验证
        if (not settings.DEBUG or not self.dev_mode) and not request.user.is_authenticated:
            return self.handle_no_permission()
        return super().dispatch(request, *args, **kwargs)


class LoginApiView(LoginRequiredMixin, APIView):
    """
    用于前端调用接口的APIView
    开放接口请勿使用
    """

    pass


class LoginModelViewSet(LoginRequiredMixin, ModelViewSet):
    """
        用于前端调用的ModelViewSet
        开放接口请勿使用
    """

    pass


class LoginUserModelViewSet(LoginRequiredMixin, UserModelViewSet):
    """
        自动保存用户信息
        用于前端调用的ModelViewSet
        开放接口请勿使用
    """

    pass

