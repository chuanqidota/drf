"""
URL configuration for drf project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.urls import path, include, re_path
from drf_yasg import openapi
from drf_yasg.views import get_schema_view
from rest_framework import permissions
from rest_framework.authentication import SessionAuthentication
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from drf import settings

urlpatterns = [
    path("", include("rest_framework.urls")),  # 登录按钮
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),  # {"username":"","password":""}
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),  # {"refresh":"上面接口返回的refresh字段"}
    path('api/user/', include('user.urls.api_urls'), name='user-api'),
]

# swagger-设置
schema_view = get_schema_view(
    openapi.Info(
        title="drf API",
        default_version='v1',
        description="drf接口文档",
    ),
    public=True,
    permission_classes=[permissions.AllowAny],
    authentication_classes=[SessionAuthentication],
    url=settings.WEB_URL
)


swagger_urlpatterns = [
    re_path('api/swagger(?P<format>\.json|\.yaml)', schema_view.without_ui(cache_timeout=0), name='schema-json'),
    path('api/swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('api/redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc')
]

urlpatterns = urlpatterns + swagger_urlpatterns

if settings.DEBUG:
    import debug_toolbar

    urlpatterns = [path('__debug__/', include(debug_toolbar.urls)), ] + urlpatterns

    urlpatterns += staticfiles_urlpatterns()  # gunicorn加载静态文件
